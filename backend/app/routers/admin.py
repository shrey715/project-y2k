from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models import User, Image, Audio
from backend.app.dependencies import get_admin_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users")
def get_all_users(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with media counts (admin only)."""
    # Subqueries for counts
    image_count_subquery = db.query(
        func.count(Image.id)
    ).filter(Image.user_id == User.id).correlate(User).scalar_subquery()
    
    audio_count_subquery = db.query(
        func.count(Audio.id)
    ).filter(Audio.user_id == User.id).correlate(User).scalar_subquery()
    
    users = db.query(
        User.id,
        User.username,
        User.email,
        image_count_subquery.label("image_count"),
        audio_count_subquery.label("audio_count")
    ).all()
    
    users_list = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "images_cnt": user.image_count or 0,
            "audios_cnt": user.audio_count or 0
        }
        for user in users
    ]
    
    return {"username": "admin", "users": users_list}


@router.get("/media")
def get_all_media(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all images and audios (admin only)."""
    images = db.query(Image).all()
    audios = db.query(Audio).all()
    
    images_list = [
        {
            "id": img.id,
            "filename": img.filename,
            "user_id": img.user_id,
            "metadata": img.file_metadata
        }
        for img in images
    ]
    
    audios_list = [
        {
            "id": aud.id,
            "filename": aud.filename,
            "user_id": aud.user_id,
            "metadata": aud.file_metadata
        }
        for aud in audios
    ]
    
    return {"images": images_list, "audios": audios_list}
