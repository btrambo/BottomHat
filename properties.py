from app import quiz_collection 

class quizInput:
    def __init__(self, title, username, options, correct):
        self.title = title
        self.username = username
        self.options = options
        self.correct_response = correct # string either option 1, option2, or option 3

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
        answers = document['answers'] #going to have 1 2 or 3

        document = quizInput(usernames,titles,questions,answers)

        arr.append(document)

    return arr