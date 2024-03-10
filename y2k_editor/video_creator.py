# Testing stuff out

from moviepy.editor import AudioFileClip, ImageSequenceClip, ImageClip, concatenate_videoclips, concatenate_audioclips, cvsecs
import numpy as np
import cv2

class Project:
    def __init__(self):
        ...

with open(r'y2k_editor/static/images/logo.png', 'rb') as file:
    image_data = file.read()
dur = 3

image_array = np.asarray(bytearray(image_data), dtype="uint8")
image_array = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)

imgclip = ImageClip(image_array, duration=cvsecs(dur))
img2 = imgclip.set_opacity(op=0.5)
video = concatenate_videoclips((imgclip, img2))

video.write_videofile('stg.mp4', fps=30)
