from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import DB_NAME, MONGO_URI

_client = None
_db = None
users_collection = None
lawyers_collection = None


def _get_db():
    global _client, _db, users_collection, lawyers_collection
    if _db is not None:
        return _db

    if not MONGO_URI:
        raise RuntimeError(
            "MONGO_URI is not set. Add it as an environment variable."
        )

    try:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        _db = _client[DB_NAME]
        users_collection = _db["users"]
        lawyers_collection = _db["lawyers"]
        users_collection.create_index("email", unique=True)
        return _db
    except PyMongoError as exc:
        raise RuntimeError(f"Failed to connect to MongoDB: {exc}") from exc


def get_users_collection():
    _get_db()
    return users_collection


def get_lawyers_collection():
    _get_db()
    return lawyers_collection
