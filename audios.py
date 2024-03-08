from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Function to establish database connection
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='projecty2k',
            user='root',
            password='vishak_30'
        )
        print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# Function to get user ID from the authentication system
def get_user_id():
    # Example: Retrieve user ID from the authentication token or session
    user_id = request.session.get('user_id')  # Example assuming user_id is stored in session
    return user_id

# Function to retrieve preloaded audio data from the database
def fetch_preloaded_audio_data(preloaded_audio_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    try:
        # Fetch preloaded audio data from the database based on the preloaded_audio_id
        cursor.execute("SELECT audio_data FROM audios WHERE id = %s AND is_preloaded = %s", (preloaded_audio_id, True))
        audio_data = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return audio_data
    except Error as e:
        print(f"Error fetching preloaded audio data: {e}")
        return None


# Function to upload audio
@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    # Get user ID from the authentication system
    user_id = get_user_id()

    # Establish database connection
    connection = connect_to_database()
    if connection is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    # Create cursor object
    cursor = connection.cursor()

    try:
        # Check if the request contains a preloaded audio ID
        if 'preloaded_audio_id' in request.form:
            preloaded_audio_id = request.form['preloaded_audio_id']
            preloaded_audio_data = fetch_preloaded_audio_data(preloaded_audio_id)

            # Insert preloaded audio data into the database with is_preloaded flag set to True
            cursor.execute("INSERT INTO audios (audio_filename, user_id, audio_data, is_preloaded) VALUES (%s, %s, %s, %s)", ('preloaded_audio.mp3', user_id, preloaded_audio_data, True))
            connection.commit()
            cursor.close()
            connection.close()

            return 'Preloaded audio uploaded successfully!'
        
        # Check if the request contains an uploaded audio file
        elif 'audio' in request.files:
            audio_file = request.files['audio']
            audio_data = audio_file.read()

            # Insert user-uploaded audio data into the database with is_preloaded flag set to False
            cursor.execute("INSERT INTO audios (audio_filename, user_id, audio_data, is_preloaded) VALUES (%s, %s, %s, %s)", (audio_file.filename, user_id, audio_data, False))
            connection.commit()
            cursor.close()
            connection.close()

            return 'User-uploaded audio uploaded successfully!'
        else:
            return 'No audio file provided in the request.', 400
    except Error as e:
        print(f"Error uploading audio to the database: {e}")
        return jsonify({'error': 'Failed to upload audio to the database'}), 500

# Route to retrieve the list of all audios from the database
@app.route('/audios', methods=['GET'])
def get_audios():
    # Establish database connection
    connection = connect_to_database()
    if connection is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    # Create cursor object
    cursor = connection.cursor()

    try:
        # Fetch both user-uploaded and preloaded audios from the database
        cursor.execute("SELECT * FROM audios")
        audios = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify(audios)
    except Error as e:
        print(f"Error fetching audios from the database: {e}")
        return jsonify({'error': 'Failed to fetch audios from the database'}), 500

if __name__ == '__main__':
    app.run(debug=True)
