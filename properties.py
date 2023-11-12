from pymongo import MongoClient
mongo_client = MongoClient('mongo')
db = mongo_client['cse312']
quiz_collection = db['quiz-questions'] # each document contains username, title, questions, correct answer
class quizInput:
    def __init__(self, title, username, options, correct, seconds, time, quiz_id, ide, showbutton, showbutton2, showbutton3, showimage, image):
        self.title = title
        self.username = username
        self.options = options
        self.correct_response = correct # string either option 1, option2, or option 3
        self.seconds = seconds
        self.time = time
        self.quiz_id = quiz_id
        self.id = ide
        self.show = showbutton
        self.show2 = showbutton2
        self.show3 = showbutton3
        self.showimage = showimage
        self.image = image

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
        seconds = document['seconds']
        time = document['time']
        quiz_id = document['quiz_id']
        showbutton = "none"
        showbutton2 = "inline-block"
        showbutton3 = "none"
        if currentuser == usernames:
            showbutton = "flex"
            showbutton2 = "none"
            showbutton3 = "block"
        try:
            image = document["image"]
            showimage = "flex"
        except:
            image = "none"
            showimage = "none"
        document = quizInput(usernames,titles,questions,answers,seconds, time, quiz_id,ide,showbutton,showbutton2, showbutton3, showimage, image)

        arr.append(document)

    return arr