import chromadb

client = chromadb.PersistentClient(path="data/vectordb")
collection = client.get_or_create_collection(name="constitution")

def get_collection():
    return collection