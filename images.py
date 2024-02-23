from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'database': 'projecty2k',
    'user': 'root',
    'password': 'vishak_30'
}

# Function to connect to MySQL database
def connect_to_database():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        print("Connected to MySQL database")
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return connection

# Route to handle image upload
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # Read image binary data
        image_data = image_file.read()

        # Insert image data into database
        cursor.execute("INSERT INTO images (filename, user_id, image_data) VALUES (%s, %s, %s)", (image_file.filename, 1, image_data))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Image uploaded successfully'}), 200
    except Error as e:
        print(f"Error uploading image to database: {e}")
        return jsonify({'error': 'Failed to upload image to database'}), 500

if __name__ == '__main__':
    app.run(debug=True)