from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models import User, Image, Audio
from backend.app.schemas import UserDetailResponse
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserDetailResponse)
def get_current_user_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user details with media counts."""
    images_count = db.query(func.count(Image.id)).filter(
        Image.user_id == current_user.id
    ).scalar()
    
    audios_count = db.query(func.count(Audio.id)).filter(
        Audio.user_id == current_user.id
    ).scalar()
    
    return UserDetailResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        images_cnt=images_count or 0,
        audios_cnt=audios_count or 0
    )


@router.get("/dashboard")
def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data for current user."""
    # Get user images
    images = db.query(Image.id, Image.filename).filter(
        Image.user_id == current_user.id
    ).all()
    images_list = [{"id": img.id, "filename": img.filename} for img in images]
    
    # Get user audios
    audios = db.query(Audio.id, Audio.filename).filter(
        Audio.user_id == current_user.id
    ).all()
    audios_list = [{"id": aud.id, "filename": aud.filename} for aud in audios]
    
    # Get default audios (from admin user id=1)
    default_audios = db.query(Audio.id, Audio.filename).filter(
        Audio.user_id == 1
    ).all()
    default_audios_list = [{"id": aud.id, "filename": aud.filename} for aud in default_audios]
    
    return {
        "username": current_user.username,
        "images": images_list,
        "audios": audios_list,
        "default_audios": default_audios_list
    }
