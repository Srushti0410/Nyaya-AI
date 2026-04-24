# AI Legal Consultant

An AI-powered legal consultant application with a FastAPI backend and a plain HTML/CSS/JS frontend.

## Project Structure

```
├── backend/       # FastAPI backend with RAG pipeline
│   ├── app/       # Application code (routes, services, models, db)
│   ├── data/      # Raw data and vector store
│   ├── scripts/   # Ingestion and test scripts
│   └── requirement.txt
│
└── frontend/      # Static frontend (HTML, CSS, JS)
    ├── home.html
    ├── chat.html
    ├── login.html
    ├── lawyers.html
    ├── profile.html
    └── styles.css
```

## Backend Setup

```bash
cd backend
pip install -r requirement.txt
uvicorn app.main:app --reload
```

## Frontend

Open any `.html` file in the `frontend/` folder directly in your browser, or serve with a static file server.

## Tech Stack

- **Backend**: FastAPI, LangChain, ChromaDB, MongoDB, OpenAI
- **Frontend**: HTML, CSS, Vanilla JavaScript
