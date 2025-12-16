from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie, Request
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User
from backend.app.utils.security import decode_access_token


def get_current_user(
    request: Request,
    access_token_cookie: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT cookie."""
    token = access_token_cookie
    
    # Also check Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


def get_current_user_optional(
    request: Request,
    access_token_cookie: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    try:
        return get_current_user(request, access_token_cookie, db)
    except HTTPException:
        return None


def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure current user is admin."""
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
