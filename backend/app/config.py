import os

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://srushtim0410_db_user:aKd5AaOUm5BjvHae@cluster0.tmuejuw.mongodb.net/?appName=Cluster0")
DB_NAME = "NyayaAI"

# FAISS paths
FAISS_INDEX_PATH = "data/vectordb/faiss.index"
METADATA_PATH = "data/vectordb/metadata.json"

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "phi"