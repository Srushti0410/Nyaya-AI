import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import query, auth

app = FastAPI(title="NyayaAI Backend")

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://nyaya-ai.vercel.app,http://localhost:3000,http://127.0.0.1:5500"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten after confirming Vercel URL
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "NyayaAI API running"}

@app.get("/health")
def health():
    import os
    groq_set = bool(os.getenv("GROQ_API_KEY"))
    mongo_set = bool(os.getenv("MONGO_URI"))
    groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    return {
        "status": "ok",
        "groq_key_set": groq_set,
        "mongo_uri_set": mongo_set,
        "groq_model": groq_model,
    }