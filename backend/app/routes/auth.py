from fastapi import APIRouter, HTTPException
from app.models.schema import LoginRequest, SignupRequest
from app.services.auth_service import create_user, verify_user

router = APIRouter()

@router.post("/signup")
def signup(user: SignupRequest):
    try:
        result = create_user(user.email, user.password)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/login")
def login(user: LoginRequest):
    try:
        result = verify_user(user.email, user.password)
        if not result["success"]:
            status_code = 404 if result["message"] == "User not found" else 401
            raise HTTPException(status_code=status_code, detail=result["message"])
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc