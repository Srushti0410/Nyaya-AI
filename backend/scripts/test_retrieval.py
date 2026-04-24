import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="data/vectordb")
collection = client.get_or_create_collection(name="constitution")

query = input("Ask something: ")

query_embedding = model.encode([query])[0].tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print("\n🔍 Results:\n")

for i in range(len(results["documents"][0])):
    print(results["metadatas"][0][i]["article"])
    print(results["documents"][0][i][:300])
    print("------")