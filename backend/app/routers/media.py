from typing import List, Optional
import json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import and_
import re
import unicodedata
from backend.app.database import get_db
from backend.app.models import User, Image, Audio
from backend.app.schemas import MediaItem
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/api/media", tags=["Media"])


def secure_filename(filename: str) -> str:
    """Secure a filename before storing it."""
    # Normalize unicode characters
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # Keep only safe characters
    filename = re.sub(r"[^\w\s\-\.]", "", filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")
    return filename or "unnamed"


@router.get("/images", response_model=List[MediaItem])
def get_user_images(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all images for current user."""
    images = db.query(Image.id, Image.filename).filter(
        Image.user_id == current_user.id
    ).all()
    return [MediaItem(id=img.id, filename=img.filename) for img in images]


@router.get("/audios", response_model=List[MediaItem])
def get_user_audios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all audios for current user."""
    audios = db.query(Audio.id, Audio.filename).filter(
        Audio.user_id == current_user.id
    ).all()
    return [MediaItem(id=aud.id, filename=aud.filename) for aud in audios]


@router.get("/images/{image_id}")
def get_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific image by ID."""
    image = db.query(Image).filter(Image.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Get content type from metadata
    content_type = "image/jpeg"
    if image.file_metadata and isinstance(image.file_metadata, dict):
        content_type = image.file_metadata.get("content-type", "image/jpeg")
    
    return Response(
        content=image.image,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=604800"}
    )


@router.get("/audios/{audio_id}")
def get_audio(
    audio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific audio by ID."""
    audio = db.query(Audio).filter(Audio.id == audio_id).first()
    
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio not found"
        )
    
    # Get content type from metadata
    content_type = "audio/mpeg"
    if audio.file_metadata and isinstance(audio.file_metadata, dict):
        content_type = audio.file_metadata.get("content-type", "audio/mpeg")
    
    return Response(
        content=audio.audio,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=604800"}
    )


@router.post("/upload")
async def upload_media(
    file_type: str = Form(...),
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload image or audio files."""
    if file_type not in ["image", "audio"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Must be 'image' or 'audio'"
        )
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded"
        )
    
    uploaded = []
    for file in files:
        filename = secure_filename(file.filename)
        file_data = await file.read()
        
        file_metadata = {
            "filename": filename,
            "user_id": current_user.id,
            "file_type": file_type,
            "content-type": file.content_type
        }
        
        if file_type == "image":
            # Check for existing file and rename if needed
            existing = db.query(Image).filter(
                and_(Image.filename == filename, Image.user_id == current_user.id)
            ).first()
            i = 1
            base_filename = filename
            while existing:
                filename = f"{base_filename}_{i}"
                existing = db.query(Image).filter(
                    and_(Image.filename == filename, Image.user_id == current_user.id)
                ).first()
                i += 1
            
            new_file = Image(
                filename=filename,
                user_id=current_user.id,
                image=file_data,
                file_metadata=file_metadata
            )
            db.add(new_file)
            
        elif file_type == "audio":
            # Check for existing file and rename if needed
            existing = db.query(Audio).filter(
                and_(Audio.filename == filename, Audio.user_id == current_user.id)
            ).first()
            i = 1
            base_filename = filename
            while existing:
                filename = f"{base_filename}_{i}"
                existing = db.query(Audio).filter(
                    and_(Audio.filename == filename, Audio.user_id == current_user.id)
                ).first()
                i += 1
            
            new_file = Audio(
                filename=filename,
                user_id=current_user.id,
                audio=file_data,
                file_metadata=file_metadata
            )
            db.add(new_file)
        
        uploaded.append(filename)
    
    db.commit()
    return {"success": True, "message": "Files uploaded successfully", "files": uploaded}


@router.delete("/images")
def delete_images(
    image_ids: str = Query(..., description="Comma-separated image IDs"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete multiple images by IDs."""
    if not image_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image IDs provided"
        )
    
    ids = [int(x.strip()) for x in image_ids.split(",")]
    
    # Check if trying to delete admin images (not allowed for non-admin)
    if current_user.username != "admin":
        admin_images = db.query(Image.id).filter(Image.user_id == 1).all()
        admin_ids = [img.id for img in admin_images]
        if all(id in admin_ids for id in ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete default images"
            )
    
    # Delete user's images
    deleted = db.query(Image).filter(
        and_(Image.id.in_(ids), Image.user_id == current_user.id)
    ).delete(synchronize_session=False)
    db.commit()
    
    return {"success": True, "message": f"Deleted {deleted} images"}


@router.delete("/audios")
def delete_audios(
    audio_ids: str = Query(..., description="Comma-separated audio IDs"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete multiple audios by IDs."""
    if not audio_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio IDs provided"
        )
    
    ids = [int(x.strip()) for x in audio_ids.split(",")]
    
    # Check if trying to delete admin audios (not allowed for non-admin)
    if current_user.username != "admin":
        admin_audios = db.query(Audio.id).filter(Audio.user_id == 1).all()
        admin_ids = [aud.id for aud in admin_audios]
        if all(id in admin_ids for id in ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete default audios"
            )
    
    # Delete user's audios
    deleted = db.query(Audio).filter(
        and_(Audio.id.in_(ids), Audio.user_id == current_user.id)
    ).delete(synchronize_session=False)
    db.commit()
    
    return {"success": True, "message": f"Deleted {deleted} audios"}
