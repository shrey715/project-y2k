from moviepy.editor import concatenate_audioclips, concatenate_videoclips, ImageClip, TextClip, CompositeVideoClip, VideoClip
from moviepy.video.fx.all import fadein, fadeout, rotate
import numpy as np
import cv2

class VideoCreator:
    def create_image_clip(self, image, duration):
        return ImageClip(image, duration=duration)

    def attach_audio_to_image_clip(self, image_clip, audio_clip):
        return image_clip.set_audio(audio_clip)

    def concatenate_image_clips(self, image_clips):
        # Ensure all clips have the same resolution
        clips_same_res = [clip.resize(height=480) for clip in image_clips]

        # Ensure all clips have the same audio sample rate
        audio_clips = [clip.audio.set_sample_width(2) for clip in clips_same_res if clip.audio is not None]

        video = concatenate_videoclips(clips_same_res)
        audio = concatenate_audioclips(audio_clips) if audio_clips else None
        return video.set_audio(audio)

    def custom_fade_in(self, clip, duration):
        return clip.fadein(duration)

    def custom_fade_out(self, clip, duration):
        return clip.fadeout(duration)
    
    def custom_slide_in(self, clip, duration):
        def make_frame(t):
            frame = clip.get_frame(t)
            width, height = frame.shape[1], frame.shape[0]
            x = max(int(width * (1 - t / duration)), 0)
            return frame[:, x:x+width]
        return VideoClip(make_frame, duration=clip.duration)

    def custom_slide_out(self, clip, duration):
        def make_frame(t):
            frame = clip.get_frame(t)
            width, height = frame.shape[1], frame.shape[0]
            x = min(int(width * (t / duration)), width)
            return frame[:, x:x+width]
        return VideoClip(make_frame, duration=clip.duration)

    def add_text_to_clip(self, clip, text, fontsize, color, position):
        text_clip = TextClip(text, fontsize=fontsize, color=color).set_position(position)
        return CompositeVideoClip([clip, text_clip])

    def clockwise_reveal(self, clip, duration):
        def make_frame(t):
            frame = clip.get_frame(t)
            width, height = frame.shape[1], frame.shape[0]
            angle = 360 * t / duration
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.ellipse(mask, (width // 2, height // 2), (width // 2, height // 2), 0, 0, angle, 255, -1)
            return cv2.bitwise_and(frame, frame, mask=mask)
        return VideoClip(make_frame, duration=clip.duration)
    
    def spin(self, clip, duration):
        return rotate(clip, lambda t: 360 * t / duration)       
    
    def add_transition(self, clip, transition, duration):
        return clip.fx(transition, duration=duration)
    
    
if __name__=='__main__':
    vc = VideoCreator()
    image_clip_1 = vc.create_image_clip('test/4.jpg', 5)
    image_clip_2 = vc.create_image_clip('test/1.jpg', 5)
    image_clip_3 = vc.create_image_clip('test/3.jpg', 5)
    
    video_clip = vc.concatenate_image_clips([image_clip_1, image_clip_2, image_clip_3])
    video_clip.write_videofile('test.mp4', fps=24)
    print('Video created successfully')
    
        