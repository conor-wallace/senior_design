from flask import Flask, render_template
from flask_ask import Ask, statement
from subprocess import Popen, PIPE
import subprocess
import sys
import time

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

@ask.intent('HandleIntent')
def HHHandle(handle):
    if handle == "pick up":
        runRosHandleScript(handle)
    elif handle == "drop":
        runRosHandleScript(handle)
    else:
        return statement("I don't know what that action is.")'''

def runRosHandleScript(requested_action):
    subprocess.Popen(['./kobuki_location.py %s' % str(requested_action)], shell=True, executable="/usr/bin/env python")
    #process = subprocess.Popen([sys.executable, 'helping_hand_launch', str(requested_object)])

def runRosScript(requested_object):
    subprocess.Popen(['./test_launch %s' % str(requested_object)], shell=True, executable="/bin/bash")
    #process = subprocess.Popen([sys.executable, 'helping_hand_launch', str(requested_object)])

if __name__ == '__main__':
    app.run(debug=True)
