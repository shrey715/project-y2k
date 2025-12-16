import os
import logging
import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, Image, Audio
from backend.app.schemas import VideoRenderRequest
from backend.app.dependencies import get_current_user
from backend.app.utils.video_creator import render_video

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video", tags=["Video"])

# Ensure temp directory exists
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)


@router.post("/render")
def render_video_endpoint(
    vid_details: VideoRenderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render video from images and audio."""
    logger.info(f"=== VIDEO RENDER REQUEST ===")
    logger.info(f"User: {current_user.username}")
    logger.info(f"Request: {vid_details}")
    
    try:
        fps = vid_details.info.get("framerate", 24)
        resolution = vid_details.info.get("resolution", [1920, 1080])
        logger.info(f"FPS: {fps}, Resolution: {resolution}")
        
        images = []
        image_durations = []
        transitions = []
        
        video_data = vid_details.video
        image_list = video_data.get("images", [])
        logger.info(f"Number of images: {len(image_list)}")
        
        for i, image_det in enumerate(image_list):
            image_id = int(image_det.get("image_id"))
            logger.info(f"  Image {i}: ID={image_id}")
            image = db.query(Image).filter(Image.id == image_id).first()
            if image:
                logger.info(f"    Found image: {image.filename}, size={len(image.image) if image.image else 0} bytes")
                images.append(image.image)
                transitions.append(image_det.get("transition", {}).get("name", "None"))
                image_durations.append(int(image_det.get("duration", 5)))
            else:
                logger.warning(f"    Image ID {image_id} not found in database!")
        
        audio = None
        audios_list = vid_details.audios or []
        logger.info(f"Number of audios: {len(audios_list)}")
        
        # Collect ALL audio files and their durations
        audio_files = []
        audio_durations = []
        for audio_item in audios_list:
            audio_id = int(audio_item.get("audio_id"))
            audio_duration = int(audio_item.get("duration", 5))  # Default 5 seconds
            logger.info(f"  Audio ID: {audio_id}, Duration: {audio_duration}s")
            audio_record = db.query(Audio).filter(Audio.id == audio_id).first()
            if audio_record and audio_record.audio:
                logger.info(f"    Found audio: {audio_record.filename}, size={len(audio_record.audio)} bytes")
                audio_files.append(audio_record.audio)
                audio_durations.append(audio_duration)
            else:
                logger.warning(f"    Audio ID {audio_id} not found!")
        
        # Pass audio files and durations to render_video
        audio_data = None
        if audio_files:
            audio_data = (audio_files, audio_durations)  # Pass as tuple
        
        if not images:
            logger.error("No valid images to render!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid images found for rendering"
            )
        
        logger.info(f"Calling render_video with {len(images)} images...")
        logger.info(f"  Durations: {image_durations}")
        logger.info(f"  Transitions: {transitions}")
        logger.info(f"  Audio data: {len(audio_files) if audio_files else 0} files")
        
        # Render video
        output_video = render_video(
            images, audio_data, image_durations, transitions, resolution, fps, TEMP_DIR
        )
        
        logger.info(f"Video rendered successfully! Size: {len(output_video)} bytes")
        
        # Save to temp file for viewing
        output_path = os.path.join(TEMP_DIR, "output_video.mp4")
        with open(output_path, "wb") as f:
            f.write(output_video)
        
        logger.info(f"Video saved to: {output_path}")
        return {"success": True, "message": "Video rendered", "url": "/api/video/view"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"=== VIDEO RENDER ERROR ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render video: {type(e).__name__}: {str(e)}"
        )


@router.get("/view")
def view_video():
    """View rendered video."""
    output_path = os.path.join(TEMP_DIR, "output_video.mp4")
    
    if not os.path.exists(output_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found. Please render a video first."
        )
    
    with open(output_path, "rb") as f:
        video_data = f.read()
    
    return Response(
        content=video_data,
        media_type="video/mp4"
    )


@router.get("/editor-data")
def get_video_editor_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data for video editor page."""
    # Get user images
    images = db.query(Image.id, Image.filename).filter(
        Image.user_id == current_user.id
    ).all()
    images_list = [{"id": img.id, "filename": img.filename} for img in images]
    
    # Get user audios + admin audios
    user_audios = db.query(Audio.id, Audio.filename).filter(
        Audio.user_id == current_user.id
    ).all()
    
    admin_audios = db.query(Audio.id, Audio.filename).filter(
        Audio.user_id == 1
    ).all()
    
    audios_list = [{"id": aud.id, "filename": aud.filename} for aud in admin_audios]
    audios_list.extend([{"id": aud.id, "filename": aud.filename} for aud in user_audios])
    
    return {
        "username": current_user.username,
        "images": images_list,
        "audios": audios_list
    }
