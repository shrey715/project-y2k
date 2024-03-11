from flask import g, Flask, render_template, request, redirect, url_for, make_response, abort, session, jsonify
from flask_jwt_extended import JWTManager, unset_jwt_cookies, create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import timedelta
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
import pymysql  
import hashlib
import os
import glob
import json

app=Flask(__name__)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_COOKIE_SECURE'] = False
app.secret_key = 'ullabritasmitafrita'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/user'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
session={'authenticated': False,'username': ''}
jwt = JWTManager(app)
csrf = CSRFProtect(app)
CORS(app)

def extractAudioFiles(connection):
    directory = 'static/audio/preloaded'
    audio_files = glob.glob(os.path.join(directory, '*.mp3'))

    try:
        with connection.cursor() as cursor:
            for audio_file in audio_files:
                filename = os.path.basename(audio_file)

                with open(audio_file, 'rb') as f:
                    audio_data = f.read()

                metadata = {}
                metadata_json = json.dumps(metadata)

                sql = "INSERT INTO `audios` (`filename`, `user_id`, `audio`, `metadata`) VALUES (%s, 1, %s, %s)"
                cursor.execute(sql, (filename, audio_data, metadata_json))
        connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")    

def db_init():
    try: 
        connection = pymysql.connect(host='localhost',
                                            user='root',
                                            password='Noshu@1211',
                                            db='y2k_database',
                                            charset='utf8mb4',
                                            cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        connection = pymysql.connect(host='localhost',
                                            user='root',
                                            password='Noshu@1211',
                                            charset='utf8mb4',
                                            cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute('CREATE DATABASE y2k_database')
            cursor.execute('USE y2k_database')
            cursor.execute('CREATE TABLE users (user_id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(100) UNIQUE, email VARCHAR(100) UNIQUE, password VARCHAR(64));')
            cursor.execute('CREATE TABLE images (image_id INT PRIMARY KEY AUTO_INCREMENT, filename VARCHAR(255) UNIQUE, user_id INT, image LONGBLOB, metadata JSON, FOREIGN KEY (user_id) REFERENCES users(user_id));')
            cursor.execute('CREATE TABLE audios (audio_id INT PRIMARY KEY AUTO_INCREMENT, filename VARCHAR(255) UNIQUE, user_id INT, audio LONGBLOB, metadata JSON, FOREIGN KEY (user_id) REFERENCES users(user_id));')
            
            username = 'admin'
            email = 'admin@y2k.com'
            hashed_password = hashlib.sha256('admin'.encode()).hexdigest()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password))
            
            audio_files = extractAudioFiles(connection)
            connection.commit()
    connection.close()
    
def getImages(username):
    with g.db.cursor() as cursor:
        sql_get_user_id = "SELECT user_id FROM users WHERE username = %s"
        cursor.execute(sql_get_user_id, (username,))
        user_id = cursor.fetchone()['user_id']

        sql_images = "SELECT * FROM images WHERE user_id = %s"
        cursor.execute(sql_images, (user_id,))
        images = cursor.fetchall()
        return images
        
def getAudios(username):
    with g.db.cursor() as cursor:
        sql_get_user_id = "SELECT user_id FROM users WHERE username = %s"
        cursor.execute(sql_get_user_id, (username,))
        user_id = cursor.fetchone()['user_id']

        sql_audios = "SELECT * FROM audios WHERE user_id = %s"
        cursor.execute(sql_audios, (user_id,))
        audios = cursor.fetchall()
        return audios
    
@app.before_request
def before_request():
    g.db = pymysql.connect(host='localhost',
                           user='root',
                           password='Noshu@1211',
                           db='y2k_database',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if session['authenticated']:
        return redirect(f'/user_dashboard/{session["username"]}')
    if request.method == 'POST':
        try:
            data = request.form
            username = data['username'] 
            password = data['password']

            if not username or not password:
                return jsonify({'status': 'error', 'message': 'Please fill in all fields'})

            with g.db.cursor() as cursor:
                sql_check_user = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql_check_user, (username,))
                result = cursor.fetchone()

                if not result:
                    return jsonify({'status': 'error', 'message': 'User does not exist'})

                hashed_password = hashlib.sha256(password.encode()).hexdigest()                
                if result['password'] == hashed_password:
                    access_token = create_access_token(identity=username, expires_delta=timedelta(days=7))
                    response = make_response(jsonify({'status': 'success', 'message': 'Login successful'}))
                    response.set_cookie('access_token_cookie', value=access_token, max_age=86400, httponly=True, path='/')
                    session['authenticated'] = True
                    session['username'] = username
                    
                    return response
                else:
                    return jsonify({'status': 'error', 'message': 'Invalid password'})
        except Exception as e:
            print("Error:", e)
            return jsonify({'status': 'error', 'message': 'Failed to login'})
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
@csrf.exempt
def logout():
    resp = make_response(redirect('/login'))
    resp.delete_cookie('access_token_cookie', path='/')
    session['authenticated'] = False
    session.pop('username', None)
    return resp

@app.route('/signup', methods=['GET', 'POST'])
@csrf.exempt
def signup():
    if session.get('authenticated', False):
        return redirect(f'/user_dashboard/{session["username"]}')
    if request.method == 'POST':
        try:
            data = request.form
            username = data['username'] 
            password = data['password']
            email = data['email']

            if not username or not password or not email:
                return jsonify({'status': 'error', 'message': 'Please fill in all fields'})

            with g.db.cursor() as cursor:
                sql_check_user = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql_check_user, (username,))
                result = cursor.fetchone()

                if result:
                    return jsonify({'status': 'error', 'message': 'User already exists'})

                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                sql_insert_user = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert_user, (username, email, hashed_password))
                g.db.commit()

                access_token = create_access_token(identity=username, expires_delta=timedelta(days=7))
                response = make_response(jsonify({'status': 'success', 'message': 'Signup successful'}))
                response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True, path='/')
                session['authenticated'] = True
                session['username'] = username
                
                return response
        except Exception as e:
            print("Error:", e)
            return jsonify({'status': 'error', 'message': 'Failed to signup'})
    return render_template('signup.html')

@app.route('/admin_dashboard/admin', methods=['GET'])
@jwt_required()
def admin_dashboard():
    if session['authenticated'] == False:
        return redirect('/login')
    current_user = get_jwt_identity()
    if current_user != 'admin':
        print("Error: Current user does not match requested user.")
        abort(403)
    users_list = []
    
    with g.db.cursor() as cursor:
        sql_get_users = "SELECT users.user_id, username, email, (SELECT COUNT(*) FROM images WHERE users.user_id = images.user_id) as image_count, (SELECT COUNT(*) FROM audios WHERE users.user_id = audios.user_id) as audio_count FROM users;"
        cursor.execute(sql_get_users)
        users_list = cursor.fetchall()
    return render_template('adminportal.html', username='admin', users=users_list)

@app.route('/user_dashboard/<username>', methods=['GET'])
@jwt_required()
def user_dashboard(username):
    if session['authenticated'] == False:
        return redirect('/login')
    current_user = get_jwt_identity()
    if current_user != username:
        print("Error: Current user does not match requested user.")
        abort(403)
    images = []
    with g.db.cursor() as cursor:
        sql_get_user_id = "SELECT user_id FROM users WHERE username = %s"
        cursor.execute(sql_get_user_id, (username,))
        user_id = cursor.fetchone()['user_id']

        default_images = getImages('admin')
        images = getImages(username)
    return render_template('home.html', username=username, images=images, default_images=default_images)

@app.route('/get_image/<image_id>', methods=['GET'])
@jwt_required()
@csrf.exempt
def get_image(image_id):
    if session['authenticated'] == False:
        return redirect('/login')
    try:
        with g.db.cursor() as cursor:
            sql_get_image = "SELECT * FROM images WHERE image_id = %s"
            cursor.execute(sql_get_image, (image_id,))
            image = cursor.fetchone()
            
            if image:
                image_data = image['image']
                metadata = json.loads(image['metadata'])
                headers = {'Content-Type': metadata['content-type']}
                return make_response(image_data, 200, headers)
            else:
                return jsonify(success=False, message="Image not found")
    except Exception as e:
        print("Error:", e)
        return jsonify(success=False, message="Failed to get image")
            
@app.route('/delete_images')
@jwt_required()
@csrf.exempt
def delete_images():
    if session['authenticated'] == False:
        return redirect('/login')
    try:
        data = request.args.get('image_ids')
        if not data:
            return jsonify(success=False, message="No image selected")
        image_ids = [int(x) for x in data.split(',')]
        
        with g.db.cursor() as cursor:
            sql_delete_images = "DELETE FROM images WHERE image_id IN %s"
            cursor.execute(sql_delete_images, (image_ids,))
            g.db.commit()
            return jsonify(success=True, message="Images deleted successfully")
    except Exception as e:
        print("Error:", e)
        return jsonify(success=False, message="Failed to delete images")
        
@app.route('/video_editor', methods=['GET'])
@jwt_required()
@csrf.exempt
def video_editor():
    if session['authenticated'] == False:
        return redirect('/login')
    image_files = getImages(session['username'])
    audio_files = getAudios(session['username'])
    return render_template('create_video.html',username=session['username'], image_files=image_files, audio_files=audio_files)

@app.route('/upload', methods=['GET','POST'])
@jwt_required()
@csrf.exempt
def upload():
    if session['authenticated'] == False:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('upload.html', username=session['username'])
    if request.method == 'POST':
        try:
            file_type = request.form.get('file_type')
            
            if file_type not in ['image', 'audio']:
                return jsonify(success=False, message="Invalid file type")

            files = request.files.getlist(file_type)

            if not files:
                return jsonify(success=False, message="No files uploaded")

            username = session.get('username')
            user_id = None
            
            with g.db.cursor() as cursor:
                sql_get_user_id = "SELECT user_id FROM users WHERE username = %s"
                cursor.execute(sql_get_user_id, (username,))
                user_id = cursor.fetchone()['user_id']

            for file in files:
                filename = secure_filename(file.filename)
                file_data = file.read()
                file_metadata = json.dumps({"filename": filename, "user_id": user_id, "file_type": file_type, "content-type": file.content_type})
                table_name = f"{file_type}s" 

                with g.db.cursor() as cursor:
                    sql_check_file = f"SELECT COUNT(*) FROM {table_name} WHERE filename = %s AND user_id = %s"
                    cursor.execute(sql_check_file, (filename, user_id))
                    count = cursor.fetchone()['COUNT(*)']

                    i = 1
                    while count > 0:
                        filename = f"{filename}_{i}"
                        cursor.execute(sql_check_file, (filename, user_id))
                        count = cursor.fetchone()['COUNT(*)']
                        i += 1

                    sql_insert_file = f"INSERT INTO {table_name} (filename, user_id, {file_type}, metadata) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql_insert_file, (filename, user_id, file_data, file_metadata))
                    print("File uploaded")
                    g.db.commit()

            return jsonify(success=True, message="Files uploaded successfully")
        except Exception as e:
            print("Error:", e)
            return jsonify(success=False, message="Failed to upload") 

@app.route('/user_details/<username>', methods=['GET'])
@jwt_required()
def user_details(username):
    if session['authenticated'] == False:
        return redirect('/login')
    current_user = get_jwt_identity()
    if current_user != username:
        print("Error: Current user does not match requested user.")
        abort(403)
    user_details = {}
    with g.db.cursor() as cursor:
        sql_get_user_id = "SELECT user_id, username, email FROM users WHERE username = %s"
        cursor.execute(sql_get_user_id, (username,))
        user_details = cursor.fetchone()
        
        sql_get_images = "SELECT count(*) FROM images WHERE user_id = %s"
        cursor.execute(sql_get_images, (user_details['user_id'],))
        images = cursor.fetchall()
        sql_get_audios = "SELECT count(*) FROM audios WHERE user_id = %s"
        cursor.execute(sql_get_audios, (user_details['user_id'],))
        audios = cursor.fetchall()
        user_details['images_cnt'] = images[0]['count(*)']
        user_details['audios_cnt'] = audios[0]['count(*)']
    return render_template('user_details.html', username=current_user, user_details=user_details)

@app.route('/images-audio-database', methods=['GET'])
@jwt_required()
def images_audio_database():
    current_user = get_jwt_identity()
    if current_user != 'admin':
        print("Error: Current user does not match requested user.")
        abort(403)
    images = []
    audios = []
    with g.db.cursor() as cursor:
        sql_images = "SELECT * FROM images"
        cursor.execute(sql_images)
        images = cursor.fetchall()
        sql_audios = "SELECT * FROM audios"
        cursor.execute(sql_audios)
        audios = cursor.fetchall()
    return render_template('images_audio_database.html', username='admin', images=images, audios=audios)

if __name__ == '__main__':
    db_init()
    app.run(debug=True)