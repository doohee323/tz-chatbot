"""Admin user registration and login (for chat gateway management)."""
import logging
import time

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_admin_required
from app.config import get_settings
from app.database import get_db
from app.models import AdminUser

router = APIRouter(prefix="/v1/admin", tags=["admin-auth"])
logger = logging.getLogger("chat_gateway")

# bcrypt max password length is 72 bytes
BCRYPT_MAX_PASSWORD = 72


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=128)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    password_confirm: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:BCRYPT_MAX_PASSWORD]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    pw = plain.encode("utf-8")[:BCRYPT_MAX_PASSWORD]
    return bcrypt.checkpw(pw, hashed.encode("utf-8"))


def _create_admin_token(username: str) -> str:
    settings = get_settings()
    payload = {"sub": username, "type": "admin", "exp": int(time.time()) + 86400}
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token.decode("utf-8") if hasattr(token, "decode") else token


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new admin user."""
    if body.password != body.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    username = body.username.strip()
    name = body.name.strip()
    email = body.email.strip().lower()
    result = await db.execute(select(AdminUser).where(AdminUser.username == username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    result = await db.execute(select(AdminUser).where(AdminUser.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    user = AdminUser(
        username=username,
        name=name,
        email=email,
        password_hash=_hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    token = _create_admin_token(username)
    logger.info("Admin registered: %s", username)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login as admin."""
    username = body.username.strip()
    result = await db.execute(select(AdminUser).where(AdminUser.username == username))
    user = result.scalar_one_or_none()
    if not user or not _verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = _create_admin_token(username)
    logger.info("Admin login: %s", username)
    return TokenResponse(access_token=token)


class ProfileResponse(BaseModel):
    username: str
    name: str
    email: str


class ProfileUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=0, max_length=128)
    email: EmailStr | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=128)
    new_password_confirm: str = Field(..., min_length=6, max_length=128)


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_admin_required),
):
    """Get current admin profile (username, name, email)."""
    result = await db.execute(select(AdminUser).where(AdminUser.username == admin_username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ProfileResponse(username=user.username, name=user.name or "", email=user.email or "")


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(
    body: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_admin_required),
):
    """Update admin profile (name, email)."""
    result = await db.execute(select(AdminUser).where(AdminUser.username == admin_username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if body.name is not None:
        user.name = body.name.strip()
    if body.email is not None:
        email = body.email.strip().lower()
        if email != (user.email or ""):
            other = (await db.execute(select(AdminUser).where(AdminUser.email == email))).scalar_one_or_none()
            if other and other.id != user.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
            user.email = email
    await db.flush()
    logger.info("Admin profile updated: %s", admin_username)
    return ProfileResponse(username=user.username, name=user.name or "", email=user.email or "")


@router.patch("/profile/password", response_model=dict)
async def change_password(
    body: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    admin_username: str = Depends(get_admin_required),
):
    """Change admin password. Requires current password."""
    if body.new_password != body.new_password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords do not match")
    result = await db.execute(select(AdminUser).where(AdminUser.username == admin_username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not _verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    user.password_hash = _hash_password(body.new_password)
    await db.flush()
    logger.info("Admin password changed: %s", admin_username)
    return {"message": "Password changed"}
