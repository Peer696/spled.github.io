import os
import re
import json
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Simple in-memory storage for demo
current_pdf_content = ""
current_pdf_filename = ""

def preprocess(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text

def text_to_chunks(text, word_length=150):
    words = text.split(' ')
    chunks = []
    
    for i in range(0, len(words), word_length):
        chunk = words[i : i + word_length]
        chunk_text = ' '.join(chunk).strip()
        if chunk_text:
            chunks.append(f'[Chunk {i//word_length + 1}] "{chunk_text}"')
    
    return chunks

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

def generate_answer(question, pdf_content):
    if not pdf_content:
        return "Please upload a PDF first."
    
    # Simple text search - find relevant chunks
    chunks = text_to_chunks(pdf_content)
    
    # Find chunks that contain question words
    question_words = question.lower().split()
    relevant_chunks = []
    
    for chunk in chunks:
        chunk_lower = chunk.lower()
        if any(word in chunk_lower for word in question_words):
            relevant_chunks.append(chunk)
    
    # If no relevant chunks found, use first few chunks
    if not relevant_chunks:
        relevant_chunks = chunks[:3]
    
    # Create prompt
    prompt = "Search results:\n\n"
    for chunk in relevant_chunks[:5]:  # Limit to 5 chunks
        prompt += chunk + "\n\n"
    
    prompt += (
        "Instructions: Answer the question using only the information from the search results above. "
        "If the information is not available in the search results, say 'Information not found in the document'. "
        "Be concise and accurate. Cite which chunk the information comes from.\n\n"
        f"Question: {question}\nAnswer:"
    )
    
    answer = generate_text(prompt)
    return answer

@app.get("/")
async def root():
    return {"message": "PDF Chatbot API is running!"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global current_pdf_content, current_pdf_filename
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # For demo purposes, we'll simulate PDF content
        # In a real app, you'd use PyMuPDF or similar
        content = await file.read()
        
        # Simulate PDF text extraction
        # This is a placeholder - in reality you'd extract actual text
        current_pdf_content = f"Sample PDF content from {file.filename}. This is a demo. The actual PDF content would be extracted here using PyMuPDF or similar library."
        current_pdf_filename = file.filename
        
        return {
            "message": "PDF uploaded and processed successfully (demo mode)", 
            "filename": file.filename,
            "note": "This is a demo version. Real PDF text extraction requires PyMuPDF installation."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/chat")
async def chat(question: str):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        answer = generate_answer(question, current_pdf_content)
        return {"answer": answer}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)