# 📚 PDF Chatbot

Een moderne PDF chatbot gebaseerd op pdfGPT, aangepast voor DeepSeek API en Supabase.

## 🚀 Quick Start

### 1. Backend Starten
```bash
cd backend
pip install -r requirements.txt
python api.py
```

### 2. Frontend Starten
```bash
cd frontend
npm start
```

### 3. Supabase Setup
1. Ga naar je Supabase dashboard
2. Voer `database_setup.sql` uit in de SQL Editor
3. Kopieer je anon key naar `frontend/.env`

## 🔧 Environment Variables

### Backend (.env)
```
DEEPSEEK_API_KEY=sk-eef8ec5ccea74da194b27a2838789d7b
SUPABASE_URL=https://ieigojplepfjuqspepmz.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
```

### Frontend (.env)
```
REACT_APP_SUPABASE_URL=https://ieigojplepfjuqspepmz.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
REACT_APP_API_URL=http://localhost:8000
```

## 📋 Features

- ✅ PDF upload en verwerking
- ✅ Semantic search met Universal Sentence Encoder
- ✅ Chat interface met DeepSeek API
- ✅ Supabase database integratie
- ✅ Page citations
- ✅ Chat geschiedenis

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python
- **Frontend:** React, TypeScript
- **Database:** Supabase
- **AI:** DeepSeek API
- **PDF Processing:** PyMuPDF
- **Embeddings:** TensorFlow Hub

## 📁 Project Structuur

```
pdf-chatbot/
├── backend/
│   ├── api.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── supabaseClient.ts
│   └── .env
└── database_setup.sql
```