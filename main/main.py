#!/usr/bin/python
import time
import urllib2
import json
from hardwareInteractions import solidEyesOnPi, turnOffEyesOnPi
#####################
# Config
#####################
workerBeeEndpoint = 'http://104.236.192.112:3001'
arbitrary = '/arbitrary'
githubWebHooks = '/github-webhooks'
pollingDelaySeconds = 10
reactionTimeHold = 120
pollStartTime = time.time()

# Action Types
eyesFlash = 'eyesFlash'
eyesSolid = 'eyesSolid'

# Setup an initial action for startup
actionData = {}
actionData["time"] = 'initialTime'
actionData["action"] = 'intitialAction'

# Setup a reaction for the IOTCat
reaction = {}
reaction["timeInSec"] = time.time()
reaction["triggeringAction"] = 'none'
reaction["type"] = 'none'
reaction["active"] = False

#######################
# Functions
#######################

# Get data from endpoint function
def getData():
    latestData = urllib2.urlopen(workerBeeEndpoint + githubWebHooks).read()
    parsedData = json.loads(latestData)["data"]
    print '\nparsedData', parsedData, '\n'
    return parsedData

# Time Since Last Poll
def timeSinceLastPoll():
    return time.time() -  pollStartTime

# Set current reaction
def setReaction(reactionType):
    reaction["timeInSec"] = time.time()
    reaction["triggeringAction"] = 'opened'
    reaction["type"] = reactionType
    reaction["active"] = True

# Perform reaction
def performReaction():
    if (reaction["type"] == eyesSolid):
        solidEyesOnPi()
    elif (reaction["type"] == eyesFlash):
        solidEyesOnPi()
        time.sleep( 1 )
        turnOffEyesOnPi()

# Turn off reactions
def turnOffReactions():
    reaction["active"] = False
    turnOffEyesOnPi()

# Check for if the reaction has been performed long enough
def reactionHasFinished():
    return (reaction["active"] == True) and ((time.time() - reaction["timeInSec"]) > reactionTimeHold)

##############################
# Main While Loop of Program
##############################
pollStartTime = time.time()
parsedData = getData()
while (True):
    print 'Current reaction: ', reaction
    
    # Get the latest data and parse the json, but only if enough time has passed
    if (timeSinceLastPoll() > pollingDelaySeconds):
        pollStartTime = time.time()
        parsedData = getData()
    
    # Check if the action is new by comparing the timestamp to the last action that we got
    if (parsedData["time"] != actionData["time"]):

        # It's new, so update our cache
        actionData = parsedData

        # Set any new actions
        if (actionData["action"] ==  'opened'):
            print 'Pull request opened! Lets turn the eyes on!'
            setReaction(eyesSolid)

        if (actionData["action"] == 'closed'):
            print 'Pull request closed! Lets flash the eyes!'
            setReaction(eyesFlash)
    
    # Perform Reaction
    if (reaction["active"] == True):
        performReaction()

    # Check if the reaction has been going on for longer than one minute and if so, turn off
    if (reactionHasFinished()):
        turnOffReactions()

    # Sleep the program for a second
    time.sleep( 1 )

