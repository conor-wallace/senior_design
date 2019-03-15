import json
from flask import Flask
from flask_ask import Ask, statement, request, session, question

app = Flask(__name__)
ask = Ask(app, '/')

@ask.launch
def launch():
    speech_text = 'Welcome to the Helping Hand, you can request an object now.'
    return statement(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('hello')
def hello():
    speech_text = 'Hello world'
    return statement(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('fetch')
def fetchObject(object):
    if object == 'cup' :
        speech_text = 'Retrieving the object'
        return statement(speech_text).simple_card('HelloWorld', speech_text)
    else:
        speech_text = 'I do not know what that object is'
        return statement(speech_text).simple_card('HelloWorld', speech_text)

if __name__ == '__main__':
    app.run(debug = True)
