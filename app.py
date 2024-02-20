from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pymysql.cursors
import hashlib

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super_secret_key'
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
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.form
            username = data['username']
            password = data['password']

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `users` WHERE `username`=%s AND `password`=%s"
                cursor.execute(sql, (username, hashed_password))
                user = cursor.fetchone()

                if user:
                    access_token = create_access_token(identity={'username': user['username'], 'email': user['email']})
                    return jsonify(authenticated=True, access_token=access_token, message="Login successful")
                else:
                    return jsonify(authenticated=False, message="Invalid username or password")

        except Exception as e:
            print("Error:", e)
            return jsonify(authenticated=False, message="Failed to process login request")

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
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

            access_token = create_access_token(identity=username)
            return jsonify(authenticated=True, access_token=access_token, message="Signup successful")
        except Exception as e:
            print("Error:", e)
            return jsonify(authenticated=False, message="Failed to signup")
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(port=5001, debug=True)