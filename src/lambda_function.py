import json
from flask import Flask
from flask_ask import Ask, statement, request, session, question

app = Flask(__name__)
ask = Ask(app, '/')

@ask.intent('hello')
def hello():
    return statement("Hello User!")

@ask.intent('fetch')
def fetchObject(object):
    if object == 'cup' :
        return statement('Retrieving the object')
    else:
        return statement('I do not know what that object is')

if __name__ == '__main__':
    app.run(debug = True)
