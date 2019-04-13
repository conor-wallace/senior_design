from flask import Flask, render_template
from flask_ask import Ask, statement
from subprocess import Popen, PIPE
import sys

app = Flask(__name__)
ask = Ask(app, '/')

@ask.intent('FetchIntent')
def HHfetch(object):

    if object == 'cup':
        runRosScript(object)
        return statement("Retrieving the " + object)
    elif object == 'bottle':
        runRosScript(object)
        return statement("Retrieving the " + object)
    elif object == 'spoon':
        runRosScript(object)
        return statement("Retrieving the " + object)
    elif object == 'bowl':
        runRosScript(object)
        return statement("Retrieving the " + object)
    elif object == 'cell phone':
        runRosScript(object)
        return statement("Retrieving the " + object)
    elif object == 'person':
        runRosScript(object)
        return statement("Retrieving the " + object)
    elif object == 'mouse':
        runRosScript(object)
        return statement("Retrieving the " + object)
    elif object == 'toothbrush':
        runRosScript(object)
        return statement("Retrieving the " + object)
    elif object == 'knife':
        runRosScript(object)
        return statement("Retrieving the " + object)
    elif object == 'fork':
        runRosScript(object)
        return statement("Retrieving the " + object)
    else:
        return statement("I don't know what that object is.")

def runRosScript(requested_object):
    process = Popen(['talker.py', 'requested_object'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

if __name__ == '__main__':
    app.run(debug=True)
