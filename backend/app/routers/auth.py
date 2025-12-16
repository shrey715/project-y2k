from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import LoginRequest, SignupRequest, MessageResponse
from backend.app.utils.security import hash_password, verify_password, create_access_token
from backend.app.dependencies import get_current_user_optional

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=MessageResponse)
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Login user and set JWT cookie."""
    # If already logged in, redirect
    if current_user:
        return MessageResponse(status="success", message="Already logged in")
    
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please fill in all fields"
        )
    
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )
    
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(hours=24)
    )
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token_cookie",
        value=access_token,
        max_age=86400,
        httponly=True,
        path="/",
        samesite="lax"
    )
    
    return MessageResponse(status="success", message="Login successful")


@router.post("/signup", response_model=MessageResponse)
def signup(
    request: SignupRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Register new user and set JWT cookie."""
    # If already logged in
    if current_user:
        return MessageResponse(status="success", message="Already logged in")
    
    if not request.username or not request.password or not request.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please fill in all fields"
        )
    
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    # Create new user
    hashed_password = hash_password(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": new_user.username},
        expires_delta=timedelta(days=7)
    )
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token_cookie",
        value=access_token,
        max_age=86400,
        httponly=True,
        path="/",
        samesite="lax"
    )
    
    return MessageResponse(status="success", message="Signup successful")


@router.get("/logout", response_model=MessageResponse)
def logout(response: Response):
    """Logout user by deleting JWT cookie."""
    response.delete_cookie(key="access_token_cookie", path="/")
    return MessageResponse(status="success", message="Logged out successfully")


@router.get("/check")
def check_auth(current_user: User = Depends(get_current_user_optional)):
    """Check if user is authenticated."""
    if current_user:
        return {"authenticated": True, "username": current_user.username}
    return {"authenticated": False, "username": None}
