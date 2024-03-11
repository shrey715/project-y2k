from moviepy.editor import ImageClip, concatenate_videoclips
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
    images.append(np.array(image))
cursor.close()
connection.close()

clips = [ImageClip(m).set_duration(2)
            for m in images]

final_video = concatenate_videoclips(clips, method="compose")
final_video.write_videofile("my_concatenation.mp4", fps=24)
