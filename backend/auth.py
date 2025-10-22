"""
JWT Authentication utilities for admin access
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production-09876543210"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing - using pbkdf2_sha256 instead of bcrypt to avoid compatibility issues
# This is still secure and suitable for production with proper configuration
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# HTTP Bearer for JWT tokens
security = HTTPBearer()


class TokenData(BaseModel):
    username: Optional[str] = None


class AdminCredentials(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Default admin credentials (in production, store in database)
# Pre-computed pbkdf2_sha256 hash for "admin123"
DEFAULT_ADMIN = {
    "username": "admin",
    "hashed_password": "$pbkdf2-sha256$29000$utdaC8F4zznHWCslBCBEiA$EgfZYglcii3ye/k/gmq4gcNBKc.gzLvTMMvchnNk7iU"  # hash of "admin123"
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using pbkdf2_sha256"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token from request"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


def authenticate_admin(username: str, password: str) -> bool:
    """Authenticate admin credentials"""
    # In production, check against database with proper password hashing
    # Using pbkdf2_sha256 for secure password verification
    if username == DEFAULT_ADMIN["username"]:
        return verify_password(password, DEFAULT_ADMIN["hashed_password"])
    return False


# Dependency for protected routes
async def require_admin(username: str = Depends(verify_token)) -> str:
    """Dependency to require admin authentication"""
    if username != DEFAULT_ADMIN["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    return username
