from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.all import loop
import pymysql
import io
from PIL import Image
import numpy as np

# Connect to the database
connection = pymysql.connect(host='localhost',
                            user='root',
                            password='Noshu@1211',
                            db='y2k_database',
                            cursorclass=pymysql.cursors.DictCursor)

images = []
cursor = connection.cursor()
cursor.execute('SELECT * FROM images')
for row in cursor:
    image = Image.open(io.BytesIO(row['image']))
    width, height = image.size
    new_height = 720
    new_width = int(new_height * width / height)
    image = image.resize((new_width, new_height))
    images.append(np.array(image, dtype=np.uint8))  # Convert to integer type
cursor.close()

# Ask the user for the duration of the transition effect
transition_duration = float(input("Enter the duration of the transition effect: "))

clips = []
for i, m in enumerate(images):
    clip = ImageClip(m).set_duration(5).fadein(transition_duration).fadeout(transition_duration)
    if i % 2 == 0:  # if the index is even
        # Create a spinning effect
        spinning_clip = CompositeVideoClip([clip.rotate(i) for i in range(360)])
        clip = loop(spinning_clip, duration=5)
    clips.append(clip)

final_video = concatenate_videoclips(clips, method="compose")

final_video.write_videofile("my_concatenation.mp4", fps=24)

connection.close()