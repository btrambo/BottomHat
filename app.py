from flask import Flask, render_template, make_response, request, send_from_directory, redirect
from pymongo import MongoClient
import bcrypt
import secrets
import hashlib

app = Flask(__name__)
mongo_client = MongoClient('mongo')
db = mongo_client['cse312']
chat_collection = db['chat']
count_collection = db['count']
auth_collection = db['auth']

if count_collection.find_one({"establish": 1}) is None:
    count_collection.insert_one({"id_count": 1})
    count_collection.insert_one({"establish": 1})


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        user = request.form.get('username_reg')
        pwd = request.form.get('password_reg')
        salt = bcrypt.gensalt()
        pwd = bcrypt.hashpw(pwd.encode(), salt)
        auth_collection.insert_one({"username": user, "password": pwd})
        return redirect('/')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        user = request.form.get('username_login')
        print(user)
        pwd = request.form.get('password_login')
        verify = auth_collection.find_one({'username': user})
        verify_pwd = verify['password']
        ser = make_response(redirect('/'))
        ser.mimetype = 'text/html'
        if bcrypt.checkpw(pwd.encode(), verify_pwd):
            token = secrets.token_urlsafe(10)
            t = hashlib.sha256(token.encode()).hexdigest()
            auth_collection.update_one({'username': user}, {'$set': {"auth": t}})
            ser.set_cookie('auth_token', value=token, max_age=3600, httponly=True)
        return ser


@app.route('/')
def server():
    if 'auth_token' in request.cookies:
        auth_token = request.cookies.get('auth_token')
        if auth_token is not None:
            hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
            check = auth_collection.find_one({"auth": hash_auth})
            if check is not None:
                user = check['username']
            else:
                user = 'Guest'
    else:
        user = 'Guest'
    print(user)
    ser = make_response(render_template('index.html', username=user))
    ser.headers['X-Content-Type-Options'] = 'nosniff'
    ser.mimetype = 'text/html'
    ser.status_code = 200
    return ser


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
