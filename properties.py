from pymongo import MongoClient
mongo_client = MongoClient('mongo')
db = mongo_client['cse312']
quiz_collection = db['quiz-questions'] # each document contains username, title, questions, correct answer
class quizInput:
    def __init__(self, title, username, options, correct, filename):
        self.title = title
        self.username = username
        self.options = options
        self.correct_response = correct # string either option 1, option2, or option 3
        self.filename = filename

def convert_mongo_to_quizInput():
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
        answers = document['answer'] # going to have 1 2 or 3
        filename = document['filename']

        document = quizInput(usernames,titles,questions,answers,filename)

        arr.append(document)

    return arr