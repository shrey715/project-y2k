from flask import Flask, render_template, request, redirect, url_for, flash, make_response, abort, session, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import timedelta
import pymysql
import hashlib

app=Flask(__name__)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_COOKIE_SECURE'] = False
app.secret_key = 'ullabritasmitafrita'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/user'
session={'authenticated': False,'username': ''}

jwt = JWTManager(app)

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
        cursor.execute('CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(100) UNIQUE, password VARCHAR(100), email VARCHAR(100) UNIQUE)')
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
                    print(access_token)
                    decoded = decode_token(access_token)
                    print(decoded)
                    response = make_response(redirect(url_for('user_dashboard', username=username)))
                    response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True, path='/')
                    print("Response header", response.headers)
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
    current_user = get_jwt_identity()
    print(current_user)
    if current_user != username:
        print("Error: Current user does not match requested user.")
        abort(403)
    return render_template('home.html',username=username)

@app.route('/video_editor', methods=['GET'])
@jwt_required()
def video_editor():
    return render_template('create_video.html')

@app.route('/upload_images', methods=['GET'])
@jwt_required()
def upload_images():
    return render_template('upload_images.html')

if __name__ == '__main__':
    app.run(port=5001, debug=True)