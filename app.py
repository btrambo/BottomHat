from flask import Flask
import temp
import json
import socketserver
import sys
from util.request import Request
from pymongo import MongoClient
import bcrypt
import secrets
from hashlib import sha256

app = Flask(__name__)

mongo_client = MongoClient("mongo")
db = mongo_client["cse-312-hw"]
chat_collection = db["chat-messages"]
user_info = db["user-credentials"]
token_storage = db["authentication-tokens"]

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
