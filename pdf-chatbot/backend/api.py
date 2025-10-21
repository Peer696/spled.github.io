import os
import re
import shutil
import urllib.request
from pathlib import Path
from tempfile import NamedTemporaryFile
import fitz
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sklearn.neighbors import NearestNeighbors
import tensorflow_hub as hub
from supabase import create_client, Client
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase setup
supabase_url = "https://ieigojplepfjuqspepmz.supabase.co"
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = None

def get_supabase_client():
    global supabase
    if supabase is None and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
    return supabase

# DeepSeek setup
openai.api_key = os.getenv("DEEPSEEK_API_KEY")
openai.api_base = "https://api.deepseek.com"

app = FastAPI(title="PDF Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = None

def preprocess(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text

def pdf_to_text(path, start_page=1, end_page=None):
    doc = fitz.open(path)
    total_pages = doc.page_count

    if end_page is None:
        end_page = total_pages

    text_list = []

    for i in range(start_page - 1, end_page):
        text = doc.load_page(i).get_text("text")
        text = preprocess(text)
        text_list.append(text)

    doc.close()
    return text_list

def text_to_chunks(texts, word_length=150, start_page=1):
    text_toks = [t.split(' ') for t in texts]
    chunks = []

    for idx, words in enumerate(text_toks):
        for i in range(0, len(words), word_length):
            chunk = words[i : i + word_length]
            if (
                (i + word_length) > len(words)
                and (len(chunk) < word_length)
                and (len(text_toks) != (idx + 1))
            ):
                text_toks[idx + 1] = chunk + text_toks[idx + 1]
                continue
            chunk = ' '.join(chunk).strip()
            chunk = f'[Page no. {idx+start_page}]' + ' ' + '"' + chunk + '"'
            chunks.append(chunk)
    return chunks

class SemanticSearch:
    def __init__(self):
        self.use = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')
        self.fitted = False

    def fit(self, data, batch=1000, n_neighbors=5):
        self.data = data
        self.embeddings = self.get_text_embedding(data, batch=batch)
        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors)
        self.nn.fit(self.embeddings)
        self.fitted = True

    def __call__(self, text, return_data=True):
        inp_emb = self.use([text])
        neighbors = self.nn.kneighbors(inp_emb, return_distance=False)[0]

        if return_data:
            return [self.data[i] for i in neighbors]
        else:
            return neighbors

    def get_text_embedding(self, texts, batch=1000):
        embeddings = []
        for i in range(0, len(texts), batch):
            text_batch = texts[i : (i + batch)]
            emb_batch = self.use(text_batch)
            embeddings.append(emb_batch)
        embeddings = np.vstack(embeddings)
        return embeddings

def load_recommender(path, start_page=1):
    global recommender
    if recommender is None:
        recommender = SemanticSearch()

    texts = pdf_to_text(path, start_page=start_page)
    chunks = text_to_chunks(texts, start_page=start_page)
    recommender.fit(chunks)
    return 'Corpus Loaded.'

def generate_text(prompt, engine="deepseek-chat"):
    try:
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model=engine,
            messages=[{"content": prompt, "role": "user"}],
            max_tokens=512,
            temperature=0.7
        )
        message = response.choices[0].message.content
    except Exception as e:
        message = f'API Error: {str(e)}'
    return message

def generate_answer(question):
    if recommender is None:
        return "Please upload a PDF first."
    
    topn_chunks = recommender(question)
    prompt = ""
    prompt += 'search results:\n\n'
    for c in topn_chunks:
        prompt += c + '\n\n'

    prompt += (
        "Instructions: Compose a comprehensive reply to the query using the search results given. "
        "Cite each reference using [ Page Number] notation (every result has this number at the beginning). "
        "Citation should be done at the end of each sentence. If the search results mention multiple subjects "
        "with the same name, create separate answers for each. Only include information found in the results and "
        "don't add any additional information. Make sure the answer is correct and don't output false content. "
        "If the text does not relate to the query, simply state 'Text Not Found in PDF'. Ignore outlier "
        "search results which has nothing to do with the question. Only answer what is asked. The "
        "answer should be short and concise. Answer step-by-step. \n\nQuery: {question}\nAnswer: "
    )

    prompt += f"Query: {question}\nAnswer:"
    answer = generate_text(prompt)
    return answer

@app.get("/")
async def root():
    return {"message": "PDF Chatbot API is running!"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), user_id: str = None):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save file temporarily
    suffix = Path(file.filename).suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    
    try:
        # Process PDF
        load_recommender(str(tmp_path))
        
        # Extract text content for database
        texts = pdf_to_text(str(tmp_path))
        content = ' '.join(texts)
        
        # Save to Supabase
        pdf_id = None
        if user_id:
            client = get_supabase_client()
            if client:
                try:
                    pdf_data = {
                        "user_id": user_id,
                        "filename": file.filename,
                        "content": content,
                        "file_size": file.size
                    }
                    
                    result = client.table("pdfs").insert(pdf_data).execute()
                    pdf_id = result.data[0]["id"] if result.data else None
                except Exception as e:
                    print(f"Supabase error: {e}")
                    pdf_id = None
        
        return {
            "message": "PDF uploaded and processed successfully", 
            "filename": file.filename,
            "pdf_id": pdf_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()

@app.post("/chat")
async def chat(question: str, user_id: str = None, pdf_id: str = None):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        answer = generate_answer(question)
        
        # Save chat to database
        if user_id and pdf_id:
            client = get_supabase_client()
            if client:
                try:
                    chat_data = {
                        "user_id": user_id,
                        "pdf_id": pdf_id,
                        "message": question,
                        "response": answer
                    }
                    
                    client.table("chats").insert(chat_data).execute()
                except Exception as e:
                    print(f"Supabase chat error: {e}")
        
        return {"answer": answer}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)