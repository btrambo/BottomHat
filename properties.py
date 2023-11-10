from pymongo import MongoClient
mongo_client = MongoClient('localhost')
db = mongo_client['cse312']
quiz_collection = db['quiz-questions'] # each document contains username, title, questions, correct answer
class quizInput:
    def __init__(self, title, username, options, correct, ide, showbutton):
        self.title = title
        self.username = username
        self.options = options
        self.correct_response = correct # string either option 1, option2, or option 3
        self.id = ide
        self.show = showbutton
        # add id to div id

def convert_mongo_to_quizInput(currentuser):
    # convert database of quiz questions into list of quizInputs format above
    
    arr = []
    # .find the documents in collection and store everything first
    # 
    data = quiz_collection.find()

    for document in data:
        # for key,value in document.items():
        usernames = document['username']
        titles = document['title']
        questions = document['options'] #options is going to have 3 values, should be able to set as a key:value with value as an arr
        answers = document['answer'] #going to have 1 2 or 3
        ide = document["id"]
        showbutton = "none"
        if currentuser == usernames:
            showbutton = "flex"
        document = quizInput(usernames,titles,questions,answers,ide,showbutton)

        arr.append(document)

    return arr