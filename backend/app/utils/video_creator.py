"""
Video creator utility - Compatible with moviepy 2.x
"""
import cv2
import numpy as np
import subprocess
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# moviepy 2.x imports
try:
    from moviepy import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips
    MOVIEPY_V2 = True
except ImportError:
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips
        MOVIEPY_V2 = False
    except ImportError:
        raise RuntimeError("moviepy is required for video rendering. Install with: pip install moviepy")


def create_transition(input_video1, input_video2, transition, output_video, duration, offset):
    """Create transition between two video clips using ffmpeg."""
    command = [
        "ffmpeg", "-y",
        "-i", input_video1,
        "-i", input_video2,
        "-filter_complex", f"xfade=transition={transition}:duration={duration}:offset={offset}",
        output_video
    ]
    subprocess.run(command, capture_output=True)


def render_video(image_list, audio, durations, transitions, quality, fps, temp_dir):
    """
    Render video from list of images with optional audio and transitions.
    
    Args:
        image_list: List of image bytes
        audio: Audio bytes or None
        durations: List of durations for each image
        transitions: List of transition names for each image
        quality: Tuple of (width, height)
        fps: Frames per second
        temp_dir: Directory for temporary files
    
    Returns:
        bytes: Rendered video data
    """
    logger.info(f"render_video called with moviepy v2: {MOVIEPY_V2}")
    
    clips = []
    quality = tuple(quality)
    
    # Set common size based on quality
    size_map = {
        (1920, 1080): (1920, 1080),
        (1280, 720): (1280, 720),
        (640, 360): (640, 360),
        (3840, 2160): (3840, 2160),
    }
    common_size = size_map.get(quality, (640, 360))
    logger.info(f"Using size: {common_size}")
    
    k = 0
    j = 0
    
    for i, image in enumerate(image_list):
        logger.info(f"Processing image {i}...")
        
        # Decode image from bytes
        image_bytearr = bytearray(image)
        image_np = np.asarray(image_bytearr, dtype=np.uint8)
        img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error(f"Error decoding image {i}")
            continue
        
        # Calculate scale factor to fit within common size
        scale_factor = min(
            common_size[0] / img.shape[1],
            common_size[1] / img.shape[0]
        )
        
        # Resize maintaining aspect ratio and convert color
        img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Create black background
        black_img = np.zeros((common_size[1], common_size[0], 3), dtype=np.uint8)
        
        # Calculate position to center image
        x_offset = (common_size[0] - img.shape[1]) // 2
        y_offset = (common_size[1] - img.shape[0]) // 2
        
        # Place image on black background
        black_img[y_offset:y_offset+img.shape[0], x_offset:x_offset+img.shape[1]] = img
        
        # Create video clip
        video_clip = ImageClip(black_img, duration=durations[i])
        
        if transitions[i] != "None":
            clip_path = os.path.join(temp_dir, f"clip{k}.mp4")
            video_clip.write_videofile(clip_path, codec="libx264", audio=False, fps=fps)
            
            if j == 0:
                vid = VideoFileClip(clip_path)
                clips.append(vid)
                k += 1
            else:
                prev_clip = os.path.join(temp_dir, f"clip{k-1}.mp4")
                output_clip = os.path.join(temp_dir, f"output_video{k}.mp4")
                create_transition(prev_clip, clip_path, transitions[i], output_clip, 1, 0)
                vid = VideoFileClip(output_clip)
                clips.append(vid)
                k += 1
        else:
            clips.append(video_clip)
        
        j += durations[i]
    
    if not clips:
        raise ValueError("No valid images to create video")
    
    logger.info(f"Concatenating {len(clips)} clips...")
    
    # Concatenate all clips
    final_clip = concatenate_videoclips(clips)
    
    # Add audio if provided
    if audio:
        logger.info("Adding audio...")
        
        # Handle tuple format: (audio_files_list, audio_durations_list)
        if isinstance(audio, tuple) and len(audio) == 2:
            audio_files, audio_durations = audio
            logger.info(f"Concatenating {len(audio_files)} audio files with durations: {audio_durations}")
            
            audio_clips = []
            for idx, audio_bytes in enumerate(audio_files):
                audio_path = os.path.join(temp_dir, f"audiofile_{idx}.mp3")
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
                clip = AudioFileClip(audio_path)
                
                # Trim to specified duration if clip is longer
                clip_duration = audio_durations[idx] if idx < len(audio_durations) else 5
                if clip.duration > clip_duration:
                    if MOVIEPY_V2:
                        clip = clip.subclipped(0, clip_duration)
                    else:
                        clip = clip.subclip(0, clip_duration)
                logger.info(f"  Audio {idx}: trimmed to {clip.duration:.1f}s")
                audio_clips.append(clip)
            
            # Concatenate all trimmed audio clips
            try:
                from moviepy import concatenate_audioclips
            except ImportError:
                from moviepy.editor import concatenate_audioclips
            
            audio_clip = concatenate_audioclips(audio_clips)
            logger.info(f"Total audio duration: {audio_clip.duration:.1f}s")
            
        elif isinstance(audio, list):
            # Old format: list of audio bytes without durations
            logger.info(f"Concatenating {len(audio)} audio files (no durations specified)...")
            audio_clips = []
            for idx, audio_bytes in enumerate(audio):
                audio_path = os.path.join(temp_dir, f"audiofile_{idx}.mp3")
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
                audio_clips.append(AudioFileClip(audio_path))
            
            try:
                from moviepy import concatenate_audioclips
            except ImportError:
                from moviepy.editor import concatenate_audioclips
            
            audio_clip = concatenate_audioclips(audio_clips)
        else:
            # Single audio file (bytes)
            audio_path = os.path.join(temp_dir, "audiofile.mp3")
            with open(audio_path, "wb") as f:
                f.write(audio)
            audio_clip = AudioFileClip(audio_path)
        
        # Trim final audio to match video duration if needed
        if final_clip.duration < audio_clip.duration:
            logger.info(f"Trimming audio to match video duration: {final_clip.duration:.1f}s")
            if MOVIEPY_V2:
                audio_clip = audio_clip.subclipped(0, final_clip.duration)
            else:
                audio_clip = audio_clip.subclip(0, final_clip.duration)
        
        # Set audio on clip (moviepy 2.x uses with_audio, 1.x uses set_audio)
        if MOVIEPY_V2:
            final_clip = final_clip.with_audio(audio_clip)
        else:
            final_clip = final_clip.set_audio(audio_clip)
    
    # Write final video
    output_path = os.path.join(temp_dir, "final_output.mp4")
    logger.info(f"Writing final video to {output_path}...")
    final_clip.write_videofile(output_path, codec="libx264", audio=True, fps=fps)
    
    logger.info("Cleaning up clips...")
    # Cleanup
    for clip in clips:
        try:
            clip.close()
        except:
            pass
    
    if audio:
        try:
            audio_clip.close()
        except:
            pass
    
    try:
        final_clip.close()
    except:
        pass
    
    # Read output video
    with open(output_path, "rb") as f:
        video_data = f.read()
    
    logger.info(f"Video rendered: {len(video_data)} bytes")
    
    # Cleanup temp files
    cleanup_files = [
        os.path.join(temp_dir, "audiofile.mp3"),
        os.path.join(temp_dir, "final_output.mp4"),
    ]
    for i in range(k):
        cleanup_files.append(os.path.join(temp_dir, f"clip{i}.mp4"))
        cleanup_files.append(os.path.join(temp_dir, f"output_video{i}.mp4"))
    
    for f in cleanup_files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except:
            pass
    
    return video_data
