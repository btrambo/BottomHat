import json
from flask import Flask, render_template, make_response, request, send_from_directory, redirect
from pymongo import MongoClient
import bcrypt
import secrets
import hashlib
from bson.json_util import dumps
import html
from properties import convert_mongo_to_quizInput, quizInput

app = Flask(__name__)
mongo_client = MongoClient('localhost')
db = mongo_client['cse312']
chat_collection = db['chat']
count_collection = db['count']
auth_collection = db['auth']
post_collection = db['post']
quiz_collection = db['quiz-questions'] # each document contains username, title, questions, correct answer

# def getuser():
#     if 'auth_token' in request.cookies:
#         auth_token = request.cookies.get('auth_token')
#         if auth_token is not None:
#             hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
#             check = auth_collection.find_one({"auth": hash_auth})
#             if check is not None:
#                 user = check['username']
#                 return user
#             else:
#                 user = 'Guest'
#                 hideheader = "none"
#                 return None
#     else:
#         user = 'Guest'
#         hideheader = "none"
#         return None

@app.route('/')
def server():
    if 'auth_token' in request.cookies:
        auth_token = request.cookies.get('auth_token')
        if auth_token is not None:
            hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
            check = auth_collection.find_one({"auth": hash_auth})
            if check is not None:
                user = check['username']
                hideheader = "block"
                currentuser = user
            else:
                user = 'Guest'
                hideheader = "none"
                currentuser = None
    else:
        user = 'Guest'
        hideheader = "none"
        currentuser = None

    quiz_list = convert_mongo_to_quizInput(currentuser)
    print(quiz_list)
    response = make_response(render_template('index.html', hider=hideheader, username=user, question_list=quiz_list))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = 'text/html'
    response.status_code = 200
    return response


@app.route('/question_form_page', methods=['GET'])
def question_form_page():
    response = make_response(render_template('create-quiz.html'))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.mimetype = 'text/html'
    response.status_code = 200
    return response


@app.route('/submit-quiz-question', methods=['POST', 'GET'])
def submit_quiz_question():
    if request.method == "POST":
        if 'auth_token' in request.cookies:
            auth_token = request.cookies.get('auth_token')
            if auth_token is not None:
                hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
                check = auth_collection.find_one({"auth": hash_auth})
                if check is not None:
                    user = check['username']
                    ide = count_collection.find_one_and_update({"name": "counter"}, {"$inc": {"count": 1}}, upsert=True, return_document=True)["count"]

                    title = html.escape(request.form.get('question-title'))
                    option1 = html.escape(request.form.get('option1'))
                    option2 = html.escape(request.form.get('option2'))
                    option3 = html.escape(request.form.get('option3'))
                    minutes = html.escape(request.form.get('minutes-input'))
                    seconds = html.escape(request.form.get('seconds-input'))
                    all_options = [option1, option2, option3]

                    quiz_collection.insert_one(
                        {"id": ide, "username": user, "title": title, "options": all_options, "minutes": minutes,"seconds": seconds, "answer":"option1"})
    return redirect('/')
@app.route('/submit-quiz-response', methods=['GET'])
def submit_quiz_response():
    print("idk")

@app.route('/post-history', methods=['GET'])
def getposts():
    mylist = list(post_collection.find({}))
    mylist.reverse()
    return make_response(dumps(mylist))


@app.route('/make-post', methods=['POST', 'GET'])
def makepost():
    if request.method == "POST":
        if 'auth_token' in request.cookies:
            auth_token = request.cookies.get('auth_token')
            if auth_token is not None:
                hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
                check = auth_collection.find_one({"auth": hash_auth})
                if check is not None:
                    user = check['username']
                    id = count_collection.find_one_and_update({"name": "counter"}, {"$inc": {"count": 1}}, upsert=True, return_document=True)["count"]
                    title = html.escape(request.form.get('post-title'))
                    message = html.escape(request.form.get('post-message'))

                    post_collection.insert_one({"id": id, "username": user, "title": title, "message": message, "likes": 0})
    return redirect('/')

@app.route('/like', methods=['POST', 'GET'])
def makelike():
    print(request)
    if request.method == "POST":
        if 'auth_token' in request.cookies:
            auth_token = request.cookies.get('auth_token')
            if auth_token is not None:
                hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
                check = auth_collection.find_one({"auth": hash_auth})
                if check is not None:
                    user = check['username']
                    idd = request.json
                    idd = json.dumps(idd)
                    print(idd)


                    try:

                        if auth_collection.find_one({"username": user})[idd] == 1:
                            auth_collection.find_one_and_update({"username": user}, {"$set": {idd: 0}})
                            post_collection.find_one_and_update({"id": int(idd)}, {"$inc": {"likes": -1}})

                        else:

                            auth_collection.find_one_and_update({"username": user}, {"$set": {idd: 1}})
                            post_collection.find_one_and_update({"id": int(idd)}, {"$inc": {"likes": 1}})

                    except:

                        auth_collection.find_one_and_update({"username": user}, {"$set": {idd: 1}})
                        post_collection.find_one_and_update({"id": int(idd)}, {"$inc": {"likes": 1}})

    return redirect('/')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        user = request.form.get('username_reg')
        user = html.escape(user)
        if user == "":
            user = "MAN WITH NO NAME"
        if user == "Guest":
            user = "I'M A LOSER"
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
        user = html.escape(user)
        pwd = request.form.get('password_login')
        verify = auth_collection.find_one({'username': user})
        try:
            verify_pwd = verify['password']
            ser = make_response(redirect('/'))
            ser.mimetype = 'text/html'
            if bcrypt.checkpw(pwd.encode(), verify_pwd):
                token = secrets.token_urlsafe(10)
                t = hashlib.sha256(token.encode()).hexdigest()
                auth_collection.update_one({'username': user}, {'$set': {"auth": t}})
                ser.set_cookie('auth_token', value=token, max_age=3600, httponly=True)
            return ser
        except:
            ser = make_response(redirect('/'))
            ser.mimetype = 'text/html'
            return ser

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
