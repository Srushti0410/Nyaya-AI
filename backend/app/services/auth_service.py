from datetime import datetime, timezone

import bcrypt
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.db.mongo import users_collection


def create_user(email: str, password: str) -> dict:
    normalized_email = email.strip().lower()

    try:
        existing_user = users_collection.find_one({"email": normalized_email})
        if existing_user:
            return {
                "success": False,
                "message": "User already exists",
            }

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        users_collection.insert_one(
            {
                "email": normalized_email,
                "password": hashed_password,
                "created_at": datetime.now(timezone.utc),
            }
        )

        return {
            "success": True,
            "message": "User created successfully",
            "user": {"email": normalized_email},
        }
    except DuplicateKeyError:
        return {
            "success": False,
            "message": "User already exists",
        }
    except PyMongoError as exc:
        raise RuntimeError(f"Database error while creating user: {exc}") from exc


def get_user(email: str) -> dict | None:
    normalized_email = email.strip().lower()

    try:
        return users_collection.find_one({"email": normalized_email})
    except PyMongoError as exc:
        raise RuntimeError(f"Database error while fetching user: {exc}") from exc


def verify_user(email: str, password: str) -> dict:
    user = get_user(email)

    if not user:
        return {
            "success": False,
            "message": "User not found",
        }

    stored_password = user.get("password")
    if not stored_password:
        return {
            "success": False,
            "message": "User record is invalid",
        }

    is_valid = bcrypt.checkpw(password.encode("utf-8"), stored_password)
    if not is_valid:
        return {
            "success": False,
            "message": "Invalid password",
        }

    return {
        "success": True,
        "message": "Login successful",
        "user": {"email": user["email"]},
    }
