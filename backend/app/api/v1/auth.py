from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional

from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    verify_token,
    SecurityUtils
)
from app.core.config import settings
from app.models.user import User
from app.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    role: str = "patient"
    rut: Optional[str] = None
    phone: Optional[str] = None

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    try:
        user_id = verify_token(token)
        user = await User.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers