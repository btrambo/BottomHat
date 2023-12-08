import json
import time

from flask import Flask, render_template, make_response, request, send_from_directory, redirect, url_for
from pymongo import MongoClient
import bcrypt
import secrets
import hashlib
from bson.json_util import dumps
import html
from properties import convert_mongo_to_quizInput, quizInput
from flask_socketio import SocketIO, send, emit
import os
import math
from werkzeug.utils import secure_filename
import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'verysecretencrypt!'
app.config['UPLOAD_PATH'] = 'static/images/'

#Comment-out the below line before running locally
socket = SocketIO(app, cors_allowed_origins="https://bottomhat.net")

#Comment-out the below line before deploying
#socket = SocketIO(app)

mongo_client = MongoClient("mongo")
db = mongo_client['cse312']
chat_collection = db['chat']
count_collection = db['count']
auth_collection = db['auth']
post_collection = db['post']
quiz_collection = db['quiz-questions'] # each document contains username, title, questions, correct answer
email_verification_tokens = db['email-tokens']
ip_collection = db['ip']

clients = []




@socket.on('connect')
def handle_connect():
   c = request.sid
   clients.append(c)


@socket.on('disconnect')
def handle_disconnect():
   c = request.sid
   clients.remove(c)


@socket.on('submit')
def handle_submit(answer):
    result = json.loads(answer)
    result = result.split(',')
    emit('test', result)
    if 'auth_token' in request.cookies:
        auth_token = request.cookies.get('auth_token')
        if auth_token is not None:
            hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
            check = auth_collection.find_one({"auth": hash_auth})
            if check is not None:
                user = check['username']
                emit('test', user)
            quiz = quiz_collection.find_one({"quiz_id": result[0]})
            if quiz is not None and quiz["status"] != "0":
                same_user = quiz['username']
                answered = check['quiz_list']
                if result[0] not in answered and user != same_user:
                    myanswers = check["questions"]
                    answered.append(result[0])
                    myanswers.append([result[0],result[1]])
                    auth_collection.update_one({'username':user}, {'$set': {"questions": myanswers}})
                    auth_collection.update_one({'username':user}, {'$set': {"quiz_list": answered}})


@socket.on('reload')
def handle_reload():
    timer = []
    count = 0
    currentuser = None
    check = None
    if count_collection.find_one() is not None:
        if 'auth_token' in request.cookies:
            auth_token = request.cookies.get('auth_token')
            if auth_token is not None:
                hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
                check = auth_collection.find_one({"auth": hash_auth})
                if check is not None:
                    currentuser = check['username']
                    # mysid = request.sid
                    # myvar = 42
                    # socket.emit('santa', myvar, to=mysid)

    quiz = convert_mongo_to_quizInput(currentuser)

    if check is not None and currentuser is not None:


        mysid = request.sid

        winners = []
        toybag = [   [    [],  [[],[]]  ],   []   ]
        # [[list of created],[list of completed]]
        # list of created in format: [[question id],[list of players]]
        # list of players in format: [player,score]
        createdquizzes = {}
        createdqlist = []
        notcreatedlost = []
        notcreatedwon = []
        winnersperquiz = {}
        answeredquestions = []

        for i in auth_collection.find_one({"username": currentuser})["quiz_list"]:
            answeredquestions.append(i)

        players = auth_collection.find()

        for i in quiz:
            if i.username == currentuser:
                createdquizzes[i.quiz_id] = i.correct_response
                createdqlist.append(i.quiz_id)
            else:
                if quiz_collection.find_one({"quiz_id": i.quiz_id})["status"] == "0":
                   if i.quiz_id in auth_collection.find_one({"username": currentuser})["quiz_list"]:
                       for ii in auth_collection.find_one({"username": currentuser})["questions"]:
                           if ii[0] == i.quiz_id and ii[1] == i.correct_response:
                               notcreatedwon.append(ii[0])
                           elif ii[0] == i.quiz_id and ii[1] != i.correct_response:
                               notcreatedlost.append(i.quiz_id)
                   else:
                        notcreatedlost.append(i.quiz_id)



        for i in players:
            ansquestions = i["questions"]
            if len(ansquestions) > 0:
                for wow in ansquestions:
                    if wow[0] in createdquizzes:
                        if createdquizzes[wow[0]] == wow[1]:
                            if wow[0] in winnersperquiz:
                                winnersperquiz[wow[0]].append((i["username"], "1"))
                            else: winnersperquiz[wow[0]] = [(i["username"], "1")]
                        else:
                            if wow[0] in winnersperquiz:
                                winnersperquiz[wow[0]].append((i["username"], "0"))
                            else: winnersperquiz[wow[0]] = [(i["username"], "0")]
        for i in createdqlist:
            for ii in players:
                if i not in ii["quiz_list"] and ii["username"] != currentuser and quiz_collection.find_one({"quiz_id": i})["status"] == "0":
                    if i in winnersperquiz:
                        winnersperquiz[i].append((ii["username"], "0"))
                    else:
                        winnersperquiz[i] = [(ii["username"], "0")]




        # myvars = json.dumps(winnersperquiz)
        # allmyquizzes = json.dumps(createdquizzes)

        tosend = [[winnersperquiz, createdqlist], [notcreatedwon, notcreatedlost], answeredquestions]

        jtosend = json.dumps(tosend)

        socket.emit('santa', jtosend, to=mysid)





    for i in quiz:
        quiz_id = i.quiz_id
        question = quiz_collection.find_one({"quiz_id": quiz_id})
        sec = int(question['seconds'])
        time1 = question['time']
        newtime = time.time()
        timeleft = question["bigtime"] - newtime
        timeleft = round(timeleft)
        ide = i.id
        if timeleft <= 0:
            totaltime = "0:00"
            quiz_collection.find_one_and_update({"quiz_id": quiz_id}, {'$set':{ "status" : '0'}})
            authors = auth_collection.find()
            for ii in authors:
                if quiz_id not in ii["quiz_list"] and i.username != ii["username"]:
                    newarr = ii["quiz_list"]
                    newarr.append(quiz_id)
                    # ii["quiz_list"] = newarr
                    auth_collection.find_one_and_update({"username": ii["username"]}, {'$set': {"quiz_list": newarr}})

                    newarr2 = ii["questions"]
                    newarr2.append([quiz_id, "noanswer"])

                    auth_collection.find_one_and_update({"username": ii["username"]}, {'$set': {"questions": newarr2}})



        else:
            min1 = math.floor(timeleft / 60)
            sec1 = timeleft - (min1 * 60)
            min2 = str(min1)

            sec2 = str(sec1)
            if sec1 < 10:
                sec2 = "0" + sec2

            totaltime = min2 + ":" + sec2

        count += 1
        timer.append([quiz_id, totaltime])
           # if sec != 0:
           #     sec -= 1
           #     minutes = int(sec/60)
           #     seconds = sec % 60
           #     if seconds < 10:
           #         time1 = str(minutes) + ':0' + str(seconds)
           #     else:
           #         time1 = str(minutes) + ':' + str(seconds)
           #     quiz_collection.update_one({'quiz_id': quiz_id}, {'$set': {"time": time1}})
           #     timer.append([quiz_id, time1])
           #     quiz_collection.update_one({'quiz_id': quiz_id}, {'$set': {"seconds": sec}})
           #     count += 1
           # else:
           #     1 + 1
            # quiz_collection.delete_one({"quiz_id": quiz_id})
               # qc = qcount_collection.find_one({})
               # q = int(qc['count'])
               # q -= 1
               # qcount_collection.update_one({}, {'$set': {"count": q}})
               # if q == 0:
               #     qcount_collection.update_one({}, {'$set': {"establish": 0}})

    if bool(timer) != False:
        timer = json.dumps(timer)
        socket.emit('render', (timer, count))

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


def get_user_credentials():
    if 'auth_token' in request.cookies:
        auth_token = request.cookies.get('auth_token')
        if auth_token is not None:
            hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
            check = auth_collection.find_one({"auth": hash_auth})
            if check is not None:
                return check
            else:
                user = 'Guest'
                return None
    else:
        user = 'Guest'
        return None

@app.route('/')
def server():
    ip = request.headers.get('Client-IP')

    if ip_collection.find_one({"ip": ip}) == None:

        t = time.time()
        x = t + 10
        y = t + 30
        ip_collection.insert_one({'ip': ip, 'amount':1, 'ban': round(y), 'time': round(x)})
    else:
        j = ip_collection.find_one({"ip": ip})
        s = j['ban']
        k = j['amount']
        t = j['time']
        k += 1
        socket.emit('test',k)
        if k > 5:
            if round(s - time.time()) > 0:
                return "Too Many Requests", 429
            else:
                ip_collection.delete_one({'ip': ip})

        else:
            if round(t - time.time()) < 10:
                ip_collection.update_one({'ip': ip}, {'$set': {"amount": k}})
            else:
                ip_collection.delete_one({'ip': ip})

    verified_email = None
    if 'auth_token' in request.cookies:
        auth_token = request.cookies.get('auth_token')
        if auth_token is not None:
            hash_auth = hashlib.sha256(auth_token.encode()).hexdigest()
            check = auth_collection.find_one({"auth": hash_auth})
            if check is not None:
                user = check['username']
                verified_email = check['email_verified']
                hideheader = "block"
                currentuser = user
                if not verified_email:
                    nov = "block"
                    yesv = "none"
                else:
                    nov = "none"
                    yesv = "block"
            else:
                user = 'Guest'
                yesv = "none"
                nov = "none"
                hideheader = "none"
                currentuser = None
    else:
        user = 'Guest'
        yesv = "none"
        nov = "none"
        hideheader = "none"
        currentuser = None

    quiz_list = convert_mongo_to_quizInput(currentuser)
    response = make_response(render_template('index.html', hider=hideheader, verified=yesv, unverified=nov, username=user, question_list=quiz_list, verified_email=verified_email))
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

                    title = html.escape(request.form.get('question-title'), quote=False)
                    option1 = html.escape(request.form.get('option1'))
                    option2 = html.escape(request.form.get('option2'))
                    option3 = html.escape(request.form.get('option3'))
                    minutes = html.escape(request.form.get('minutes-input'))
                    seconds = html.escape(request.form.get('seconds-input'))
                    answer = request.form.get("answer")
                    all_options = [option1, option2, option3]
                    # if seconds == "":
                    #     seconds = 0
                    # if minutes == "":
                    #     minutes = 0
                    if seconds.isnumeric() == False:
                        seconds = "0"
                    if minutes.isnumeric() == False:
                        minutes = "0"
                    mytime = time.time()
                    mymin = float(minutes) * 60
                    futuretime = float(mymin) + float(seconds) + mytime

                    if len(seconds) == 1:
                       time1 = minutes + ":0" + seconds
                    else:
                       time1 = minutes + ":" + seconds
                    seconds = int(minutes) * 60 + int(seconds)
                    idc = count_collection.find_one({})

                    c = int(idc['count'])



                    c = "quiz_" + str(c)
                    myfile = request.files['image-input']
                    if "image-input" in request.files and myfile.filename != "" and myfile.filename:




                        fname = "quizimage" + str(ide) + ".jpg"

                        myfile.save(os.path.join(app.config['UPLOAD_PATH'], fname))
                        path = "static/images/" + fname
                        # myfile.save(path)
                        quiz_collection.insert_one(
                            {"id": ide, "image": path, "username": user, "title": title, "options": all_options, "time": time1, "seconds": seconds, "bigtime": futuretime, "status": 1, "quiz_id": c, "answer":"option" + answer})
                    else:
                        quiz_collection.insert_one(
                            {"id": ide, "username": user, "title": title, "options": all_options, "time": time1, "seconds": seconds, "bigtime": futuretime, "status": 1, "quiz_id": c, "answer":"option" + answer})
    return redirect('/')


# @app.route('/post-history', methods=['GET'])
# def getposts():
#     mylist = list(post_collection.find({}))
#     mylist.reverse()
#     print("test1")
#     return make_response(dumps(mylist))

# @app.route('/static/images', methods=['GET'])
# def double_secure_image():
#     print(request.path)
#     print("test2")
#     return

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
        auth_collection.insert_one({"username": user, "password": pwd, 'questions': [], 'quiz_list': [], "email_verified": False})
        return redirect('/')


@app.route('/send_email', methods=['POST', 'GET'])
def send_email():
    if request.method == "POST":
        user_email = request.form.get('email-input')
        user_credentials = get_user_credentials()
        # send the email
        token = secrets.token_urlsafe(80)
        email_verification_tokens.insert_one({"user": user_credentials['username'], "token":token})

        myurl = f"https://bottomhat.net/verify_email/{token}"

        message = {
            "from_email": "verify@bottomhat.net",
            "subject": "Please verify your email",
            "text": f'To verify your email, click the following link: {myurl}',
            "to": [{"email": user_email}],
        }
        try:
            mailchimp = MailchimpTransactional.Client(secretkey)
            response = mailchimp.messages.send({"message": message})
            print('API called successfully: {}'.format(response))
            ser = make_response(redirect('/'))
            ser.mimetype = 'text/html'
            return ser
        except ApiClientError as error:
            print('An exception occurred: {}'.format(error.text))


@app.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    email_token_document = email_verification_tokens.find_one({"token": token})
    username = email_token_document['user']
    auth_collection.update_one({'username': username}, {'$set': {"email_verified": True}})
    ser = make_response(redirect('/'))
    ser.mimetype = 'text/html'
    return ser


# @app.route('/static/<path>', methods=['GET', "POST"])
# def set_sniff(path):
#     filetype = path.split('.')[-1]
#
#     if (filetype == "css"):
#         response = make_response(render_template('create-quiz.html'))
#         response.headers['X-Content-Type-Options'] = 'nosniff'
#         response.mimetype = 'text/html'
#         response.status_code = 200
#         return response
#
#         response.headers['X-Content-Type-Options'] = 'nosniff'

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


@app.after_request
def set_secure_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8080)
    socket.run(app, debug=True, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
    #socket.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
