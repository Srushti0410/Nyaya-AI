from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import DB_NAME, MONGO_URI


def _create_mongo_client() -> MongoClient:
	if not MONGO_URI:
		raise RuntimeError("MONGO_URI is not set. Provide your MongoDB Atlas connection string in environment variables.")

	try:
		mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
		mongo_client.admin.command("ping")
		return mongo_client
	except PyMongoError as exc:
		raise RuntimeError(f"Failed to connect to MongoDB: {exc}") from exc


client = _create_mongo_client()
db = client[DB_NAME]

users_collection = db["users"]
lawyers_collection = db["lawyers"]

users_collection.create_index("email", unique=True)