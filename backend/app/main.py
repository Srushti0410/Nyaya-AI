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