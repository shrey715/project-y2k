from flask import Flask, render_template, request, redirect, url_for, flash, make_response, abort
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import timedelta
import mysql.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

app=Flask(__name__)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_COOKIE_SECURE'] = False # Only for development, set to True for production
app.secret_key = 'your_secret_key_here'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/user'

jwt = JWTManager(app)

conn = mysql.connector.connect(
    host="localhost",
    user="user",
    password="password",
    database="database"  
)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    cookie_path = '/'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['Password']

        if username == 'admin' and password == 'admin':
            return redirect(url_for('user_list'))

        cur=conn.cursor()
        cur.execute("SELECT * FROM userdetails WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        stored_password=user[3]
        password_verified=verify_password(password,stored_password)
        if user and password_verified:
            access_token = create_access_token(identity=username, expires_delta=timedelta(days=7))
            print(access_token)
            decoded = decode_token(access_token)
            print(decoded)
            response = make_response(redirect(url_for('user_detail', user_id=username)))
            cookie_path = '/' 
            response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True, path=cookie_path)
            print("Response header", response.headers)
            return response
        
        flash('Invalid email or password', 'error')

    return render_template('login.html')

def verify_password(password, stored_password):
    salt = b'salt_123' 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    derived_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return derived_key == stored_password

@app.route('/user_list')
def user_list():
    try:
        
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM userdetails")

        usernames = [row[0] for row in cursor.fetchall()]

        cursor.close()
        
        return render_template('user_list.html', usernames=usernames)
    except mysql.connector.Error as err:
        return f"Error: {err}"

@app.route('/signuppage')
def signuppage():
    return render_template('signup.html')

@app.route('/user_detail/<user_id>')
@jwt_required()
def user_detail(user_id):
    current_user = get_jwt_identity()
    print("Current user:", current_user)
    if current_user != user_id:
        print("Error: Current user does not match requested user.")
        abort(403)  
    
    cur=conn.cursor()
    cur.execute("SELECT * FROM userdetails WHERE username = %s", (current_user,))
    user = cur.fetchone()
    cur.close()
    if user:
        return render_template('welcome.html', username=user[1])
    else:
        return "User not found"
    
def hash_password(password):
    salt = b'salt_123' 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    hashed_password = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return hashed_password
    
@app.route('/signup', methods=['GET', 'POST'])
def registration():
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['emailId']
        password = request.form['Password']
        confirm_password=request.form['confirm_password']

        if username=='admin' or password=='admin':
            flash("Username and password cannot be 'admin'. Please choose another",'Alert') 
            return render_template('signup.html')

        if password!=confirm_password:
            flash("Passwords do not match. Please enter the same password in both the fields.",'Alert')
            return render_template('signup.html')

        hashed_password = hash_password(password)

        try:
            cur=conn.cursor()
            cur.execute("SELECT * FROM userdetails WHERE username= %s",(username,))
            existing_user=cur.fetchone()
            
            if existing_user:
                flash("Username already exists. Please choose another username.",'Alert')
                return render_template('signup.html')
            else:
                cur.execute("INSERT INTO userdetails (username, email, hashed_password) VALUES (%s, %s, %s)", (username, email, hashed_password))
                conn.commit()
                cur.close()
        
                return redirect(url_for('loginpage'))
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
