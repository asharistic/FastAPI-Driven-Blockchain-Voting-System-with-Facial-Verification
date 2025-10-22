"""
Authentication routes for admin login
"""
from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from backend.auth import (
    AdminCredentials,
    Token,
    authenticate_admin,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(credentials: AdminCredentials):
    """Admin login endpoint"""
    if not authenticate_admin(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": credentials.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/verify")
async def verify_token_endpoint(token: str):
    """Verify if a token is valid"""
    try:
        from backend.auth import verify_token
        from fastapi.security import HTTPAuthorizationCredentials
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        username = verify_token(credentials)
        return {"valid": True, "username": username}
    except:
        return {"valid": False}
