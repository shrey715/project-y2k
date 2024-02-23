from flask import Flask, render_template, request, redirect, url_for, make_response, abort, session, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.utils import secure_filename
import pymysql  
import hashlib
import base64

app=Flask(__name__)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_COOKIE_SECURE'] = False
app.secret_key = 'ullabritasmitafrita'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/user'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['SESSION_COOKIE_DOMAIN'] = 'localhost' 
session={'authenticated': False,'username': ''}
jwt = JWTManager(app)
csrf = CSRFProtect(app)

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
        cursor.execute('CREATE TABLE images (image_id INT PRIMARY KEY AUTO_INCREMENT, filename VARCHAR(255), user_id INT, image LONGBLOB, metadata TEXT, FOREIGN KEY (user_id) REFERENCES users(user_id));')
        cursor.execute('CREATE TABLE audios (audio_id INT PRIMARY KEY AUTO_INCREMENT, filename VARCHAR(255), user_id INT, audio LONGBLOB, metadata TEXT, FOREIGN KEY (user_id) REFERENCES users(user_id));')
        connection.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session['authenticated']:
        return redirect(f'/user_dashboard/{session["username"]}')
    if request.method == 'POST':
        try:
            data = request.form
            username = data['username'] 
            password = data['password']

            if not username or not password:
                return jsonify(authenticated=False, message="Please fill in all fields")

            with connection.cursor() as cursor:
                sql_check_user = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql_check_user, (username,))
                result = cursor.fetchone()

                if not result:
                    return jsonify(authenticated=False, message="Username does not exist")

                hashed_password = hashlib.sha256(password.encode()).hexdigest()                
                if result['password'] == hashed_password:
                    access_token = create_access_token(identity=username, expires_delta=timedelta(days=7))
                    decoded = decode_token(access_token)
                    response = make_response(redirect(url_for('user_dashboard', username=username)))
                    response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True, path='/')
                    session['authenticated'] = True
                    session['username'] = username
                    
                    return response
                else:
                    return jsonify(authenticated=False, message="Incorrect password")
        except Exception as e:
            print("Error:", e)
            return jsonify(authenticated=False, message="Failed to login")                    
    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        try:
            data = request.form
            username = data['username']
            password = data['password']
            email = data['email']

            if not username or not password or not email:
                return jsonify(authenticated=False, message="Please fill in all fields")

            with connection.cursor() as cursor:
                sql_check_username = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql_check_username, (username,))
                result_username = cursor.fetchone()

                if result_username:
                    return jsonify(authenticated=False, message="Username is already taken")

                sql_check_email = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql_check_email, (email,))
                result_email = cursor.fetchone()

                if result_email:
                    return jsonify(authenticated=False, message="Email is already taken")

                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                sql_insert_user = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert_user, (username, hashed_password, email))
                connection.commit()

            return jsonify(authenticated=True, message="Signup successful")
        except Exception as e:
            print("Error:", e)
            return jsonify(authenticated=False, message="Failed to signup")

    return render_template('signup.html')

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
    with connection.cursor() as cursor:
        sql_get_user_id = "SELECT user_id FROM users WHERE username = %s"
        cursor.execute(sql_get_user_id, (username,))
        user_id = cursor.fetchone()['user_id']

        sql_get_images = "SELECT * FROM images WHERE user_id = %s"
        cursor.execute(sql_get_images, (user_id,))
        images = cursor.fetchall()
    return render_template('home.html', username=username, images=images)

@app.route('/get_image/<image_id>', methods=['GET'])
@jwt_required()
@csrf.exempt
def get_image(image_id):
    if session['authenticated'] == False:
        return redirect('/login')
    try:
        with connection.cursor() as cursor:
            sql_get_image = "SELECT * FROM images WHERE image_id = %s"
            cursor.execute(sql_get_image, (image_id,))
            image = cursor.fetchone()
            
            if image:
                image_data = image['image']
                headers = {'Content-Type': 'image/' + image['filename'].split('.')[-1]} 
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
            
            with connection.cursor() as cursor:
                sql_get_user_id = "SELECT user_id FROM users WHERE username = %s"
                cursor.execute(sql_get_user_id, (username,))
                user_id = cursor.fetchone()['user_id']

            for file in files:
                print(1)
                filename = secure_filename(file.filename)
                file_data = file.read()
                file_metadata = file.content_type
                table_name = f"{file_type}s" 
                
                with connection.cursor() as cursor:
                    sql_insert_file = f"INSERT INTO {table_name} (filename, user_id, {file_type}, metadata) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql_insert_file, (filename, user_id, file_data, file_metadata))
                    print("File uploaded")
                    print(sql_insert_file, (filename, user_id, file_data, file_metadata))
                    connection.commit()

            return jsonify(success=True, message="Files uploaded successfully")
        
        except Exception as e:
            print("Error:", e)
            return jsonify(success=False, message="Failed to upload")

    
        
if __name__ == '__main__':
    app.run(port=5001, debug=True)