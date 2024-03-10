from flask import g, Flask, render_template, request, redirect, url_for, make_response, abort, session as sesh, jsonify
from flask_jwt_extended import JWTManager, unset_jwt_cookies, create_access_token, jwt_required, get_jwt_identity, decode_token
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from urllib.parse import quote_plus as _parse_quote_plus
import pymysql  
import hashlib
import os
import glob
import json
import y2k_editor.db_credentials as _dbcred     # MySQL credentials
# import y2k_editor.video_creator as vc

# BIG TODO Refactor


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
jwt = JWTManager(app)
csrf = CSRFProtect(app)
CORS(app)

session={'authenticated': False,'username': ''}     #f00 BIG TODO CHANGE!

# -----
"""
The `db_credentials.py` module contains the credentials for the MySQL server
running on the system. Each dev machine needs to have its own module with its
respective MySQL credentials set up in the file.

To do this, create the file `db_credentials.py` (in the same directory as this module).
Check the sample file `db_credentials.sample.py` for the expected format of the file.

Note: IRead the note in `db_credentials.sample.py`
"""
# Uncomment the 5 lines below to enable SQLAlchemy implementation (changes nothing for now)

# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{_dbcred.username}:{_parse_quote_plus(_dbcred.password)}@localhost/{_dbcred.db_name}'
# db = SQLAlchemy(app)

# from y2k_editor.models import User, Audio, Image, DBProject
# with app.app_context():
    # db.create_all()

# -----

### BIG TODO REFACTORRR


def loadPreloadedLibrary(connection):
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
                                            user=_dbcred.username,
                                            password=_dbcred.password,
                                            db='y2k_database',  # Uses the same old name
                                            charset='utf8mb4',
                                            cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        connection = pymysql.connect(host='localhost',
                                            user=_dbcred.username,
                                            password=_dbcred.password,
                                            charset='utf8mb4',
                                            cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute('CREATE DATABASE y2k_database')
            cursor.execute('USE y2k_database')
            cursor.execute('CREATE TABLE users (user_id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(100) UNIQUE, email VARCHAR(100) UNIQUE, password VARCHAR(64));')
            cursor.execute('CREATE TABLE images (image_id INT PRIMARY KEY AUTO_INCREMENT, filename VARCHAR(255), user_id INT, image LONGBLOB, metadata JSON, FOREIGN KEY (user_id) REFERENCES users(user_id));')
            cursor.execute('CREATE TABLE audios (audio_id INT PRIMARY KEY AUTO_INCREMENT, filename VARCHAR(255), user_id INT, audio LONGBLOB, metadata JSON, FOREIGN KEY (user_id) REFERENCES users(user_id));')
            
            username = 'admin'
            email = 'admin@y2k.com'
            hashed_password = hashlib.sha256('admin'.encode()).hexdigest()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password))
            
            loadPreloadedLibrary(connection)
            connection.commit()
    connection.close()
    
@app.before_request
def before_request():
    g.db = pymysql.connect(host='localhost',
                           user='root',
                           password='agn@Nadu.1711',
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

@app.before_request
def testing():
    print(list(sesh.items()))
    ...

@app.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    cookie = request.cookies.get('access_token_cookie')
    print('cookie:', cookie)
    if cookie:
        token = decode_token(cookie)
        print('token:', token)
        return redirect(f"user_dashboard")
    
    # if session['authenticated']:
    #     return redirect(f'/user_dashboard')
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
                    expireTime = 86400
                    access_token = create_access_token(identity=username, expires_delta=timedelta(seconds=expireTime))
                    response = make_response(jsonify({'status': 'success', 'message': 'Login successful'}))
                    response.set_cookie('access_token_cookie', value=access_token, max_age=expireTime, httponly=True, path='/')

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
    cookie = request.cookies.get('access_token_cookie')
    print('cookie:', cookie)
    if cookie:
        token = decode_token(cookie)
        print('token:', token)
        return redirect(f"user_dashboard")
    
    # if session.get('authenticated', False):
    #     return redirect(f'/user_dashboard')
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
        sql_get_users = "SELECT users.user_id, username, email, count(images.user_id) as image_count, count(audios.user_id) as audio_count FROM users LEFT JOIN images ON users.user_id = images.user_id LEFT JOIN audios ON users.user_id = audios.user_id GROUP BY users.user_id"
        cursor.execute(sql_get_users)
        users_list = cursor.fetchall()
    return render_template('adminportal.html', username='admin', users=users_list)


@app.route('/user_dashboard', methods=['GET'])
@jwt_required()
def user_dashboard():
    cookie = request.cookies.get('access_token_cookie')
    # print('cookie:', cookie)
    if not cookie:
        return redirect('login')

    # if session['authenticated'] == False:
    #     return redirect('/login')
    
    username = get_jwt_identity()
    # username = decode_token(cookie).get('sub')
    # if current_username != username:
    #     print("Error: Current user does not match requested user.")
    #     abort(403)
    images = []
    with g.db.cursor() as cursor:
        sql_get_user_id = "SELECT user_id FROM users WHERE username = %s"
        cursor.execute(sql_get_user_id, (username,))
        user_id = cursor.fetchone()['user_id']

        sql_default_images = "SELECT * FROM images WHERE user_id = 1"
        sql_get_images = "SELECT * FROM images WHERE user_id = %s"
        cursor.execute(sql_get_images, (user_id,))
        images = cursor.fetchall()
        cursor.execute(sql_default_images)
        default_images = cursor.fetchall()
    return render_template('home.html', username=username, images=images, default_images=default_images)

@app.route('/get_image/<image_id>', methods=['GET'])
@jwt_required()
@csrf.exempt
def get_image(image_id):
    cookie = request.cookies.get('access_token_cookie')
    # print('cookie:', cookie)
    if not cookie:
        return redirect('login')
    
    # if session['authenticated'] == False:
    #     return redirect('/login')
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

@app.route('/video_editor', methods=['GET'])
@jwt_required()
@csrf.exempt
def video_editor():
    if session['authenticated'] == False:
        return redirect('/login')
    return render_template('create_video.html',username=session['username'])

@app.route('/upload', methods=['GET','POST'])
@jwt_required()
@csrf.exempt
def upload():
    # if session['authenticated'] == False:
    #     return redirect('/login')
    
    cookie = request.cookies.get('access_token_cookie')
    if not cookie:
        return redirect('login')
    
    username = decode_token(cookie).get('sub')
    if request.method == 'GET':
        return render_template('upload.html', username=username)
    if request.method == 'POST':
        try:
            file_type = request.form.get('file_type')
            
            if file_type not in ['image', 'audio']:
                return jsonify(success=False, message="Invalid file type")

            files = request.files.getlist(file_type)

            if not files:
                return jsonify(success=False, message="No files uploaded")

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
