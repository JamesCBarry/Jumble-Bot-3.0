#This is a new Jumble Bot Build

## IMPORT Files
from cgitb import text
from collections import UserDict
from getpass import getuser
from multiprocessing.dummy import active_children
from operator import length_hint
from pathlib import Path
from pyexpat.errors import messages
from socket import EAI_SOCKTYPE
from turtle import setposition, update
from dotenv import load_dotenv
import pickle
import slack
import time
from urllib.request import Request, urlopen
import random
from random import shuffle
import datetime

## This is an example Slack Result used in testing

# Below is the info required to run your BAT file, link to your Slack Instance (which must be approved via Slack APIs), and set the points for each difficulty
conversation_id = "xxx"
SLACK_TOKEN = 'xxxx-1111111111111-1111111111111-111111111111111111111111'
easyPoint = 1
mediumPoint = 3
hardPoint = 5
slackchannel = '#Riddles'

client = slack.WebClient(SLACK_TOKEN)

# This pulls in the words for the jumblebot

url = "https://raw.githubusercontent.com/openethereum/wordlist/master/res/wordlist.txt"
req = Request(url)
web_byte = urlopen(req).read()

webpage = web_byte.decode('utf-8')
fulllist = webpage.split("\n")

########### NEW JUMBLE FUNCTIONS ##############

### JUMBLE WORD FUNCTIONS ###

# Builds the word list based on 3 constraints
def pickWords(minlength, maxlength, words):
    wordlist = [word for word in fulllist if len (word) in range(minlength, maxlength)]
    return(random.sample(wordlist, words))

# Returns a jumbled list of words
def jumbleWords(words):
    jumbledwords = ([0] * len(words))
    for x in range(len(words)):
        wordlist = list(words[x])
        shuffle(wordlist)
        jumbledwords[x] = ''.join(wordlist)
    return jumbledwords

# Combiles all the jumbled words together
def compileWords(easyJumble, mediumJumble, hardJumble):
    textOutput = ('Easy Jumbles (1 point):' + '\n')
    for x in range(len(easyJumble)):
        textOutput += str(x + 1) + ". " + easyJumble[x] + '\n'
    textOutput += ('\n' + 'Medium Jumbles (3 points):' + '\n')
    for x in range(len(mediumJumble)):
        textOutput += str(x + 1) + ". " + mediumJumble[x] +'\n'
    textOutput += ('\n' + 'Hard Jumbles (5 points):' + '\n')
    for x in range(len(hardJumble)):
        textOutput += str(x + 1) + ". " + hardJumble[x] +'\n'
    return textOutput

# When a certain # of words are left in the jumble, this will reprint the current words
def checkJumbleReminder(fullkey, cutoff1, cutoff2, cutoff3, easyJumble, mediumJumble, hardJumble):
    remainingJumbles = len(fullkey)
    if remainingJumbles == (cutoff1):
        textOutput = "Remaining jumbles are: '\n\n'" + compileWords(easyJumble, mediumJumble, hardJumble)
        printToSlack(textOutput)
    if remainingJumbles == (cutoff2):
        textOutput = "Remaining jumbles are: '\n\n'" + compileWords(easyJumble, mediumJumble, hardJumble)
        printToSlack(textOutput)
    if remainingJumbles == (cutoff3):
        textOutput = "Remaining jumbles are: '\n\n'" + compileWords(easyJumble, mediumJumble, hardJumble)
        printToSlack(textOutput) 

# Rebuilds the compiled word list with the remaining jumbles
def updateCompiledWords(easyJumble, mediumJumble, hardJumble):
    textOutput = "Remaining jumbles are: '\n\n'" + compileWords(easyJumble, mediumJumble, hardJumble)
    return textOutput

# Returns what key the guess is in, along with the corresponding points
def checkKey(guess, easyKey, mediumKey, hardKey):
    if guess in easyKey:
        return easyPoint
    elif guess in mediumKey:
        return mediumPoint
    elif guess in hardKey:
        return hardPoint

# Removes jumbles from the full key, the specific key, and the jumble list
def removeWords(guess, fullKey, easyJumble, easyKey, mediumJumble, mediumKey, hardJumble, hardKey):
    fullKey.remove(guess)
    if guess in easyKey:
        easyJumble.remove(easyJumble[easyKey.index(guess)])
        easyKey.remove(guess)
    if guess in mediumKey:
        mediumJumble.remove(mediumJumble[mediumKey.index(guess)])
        mediumKey.remove(guess)
    if guess in hardKey:
        hardJumble.remove(hardJumble[hardKey.index(guess)])
        hardKey.remove(guess)

### LEADERBOARD MANGEMENT FUNCTIONS ###

# Returns the current user dictionary
# Returns the current user dictionary
def getUserDictionary():
    userDicFileR = open("pickleFiles/userdictionary", "rb")
    userDic = pickle.load(userDicFileR)
    userDicFileR.close()
    return userDic

# Matches a name to the userID. If there is no userID, it adds it to the dictionary.
def findUserName(userDic, userID):
    if userID in userDic:
        name = userDic[userID]
        return name, userDic
    else:
        name, userDic = addUserToDictionary(userID)        
        return name, userDic

# Adds a new user to the dictionary and returns updated dictionary
def addUserToDictionary(userID):
    userDic = getUserDictionary()
    userinfo = client.users_info(user=userID)
    name = userinfo['user']['name']

    userIDFile = open("pickleFiles/userdictionary", 'wb')
    userDic[userID] = name
    print(name + " was added to the User Dictionary")
    pickle.dump(userDic, userIDFile)
    userIDFile.close()
    return name, userDic

def saveUserDictionary(dictionary):
    userIDFileW = open("pickleFiles/userdictionary", 'wb')
    pickle.dump(dictionary, userIDFileW)
    userIDFileW.close()

# Returns the current daily leaderboard
def getDailyLeaderboard():
    dailyLeaderboardFileR = open("pickleFiles/dailyLeaderboard", "rb")
    dailyLeaderboard = pickle.load(dailyLeaderboardFileR)
    dailyLeaderboardFileR.close()
    return dailyLeaderboard
    
# Adds score to the daily leaderboard
def updateDailyLeaderboard(winner_name, dailyLeaderboard, pointValue):
    if winner_name in dailyLeaderboard:
        dailyLeaderboard[winner_name] = dailyLeaderboard[winner_name] + pointValue
    else:        
        dailyLeaderboard[winner_name] = pointValue

# Saves the daily leaderboard
def saveDailyLeaderboard(dailyLeaderboard):
    dailyLeaderboardFileW = open("pickleFiles/dailyLeaderboard", "wb")
    pickle.dump(dailyLeaderboard, dailyLeaderboardFileW)
    dailyLeaderboardFileW.close()

#Set all the scores to zero while saving the names in the dictionary.
def resetDailyLeaderboard():
    dailyLeaderboardFileR = open("pickleFiles/dailyLeaderboard", "rb")
    dailyLeaderboard = pickle.load(dailyLeaderboardFileR)
    for key, value in dailyLeaderboard.items():
        dailyLeaderboard[key] = 0
    dailyLeaderboardFileR.close()
    
    dailyLeaderboardFileW = open("pickleFiles/dailyLeaderboard", "wb")
    pickle.dump(dailyLeaderboard, dailyLeaderboardFileW)
    dailyLeaderboardFileW.close()

# Gets weekly leaderboard
def getWeeklyLeaderboard():    
    weeklyLeaderboardFileR = open("pickleFiles/weeklyLeaderboard", "rb")
    weeklyLeaderboard = pickle.load(weeklyLeaderboardFileR)
    weeklyLeaderboardFileR.close()
    return weeklyLeaderboard

#Determines the winner of the daily leaderboard
def calculateDailyLeaderboardWinner():
    dailyLeaderboardFileR = open("pickleFiles/dailyLeaderboard", "rb")
    dailyLeaderboard = pickle.load(dailyLeaderboardFileR)
    winner_name = max(dailyLeaderboard, key=dailyLeaderboard.get)
    dailyLeaderboardFileR.close()
    return winner_name    

# Adds score to the weekly leaderboard
def updateWeeklyLeaderboard(winner_name, weeklyLeaderboard):
    if winner_name in weeklyLeaderboard:
        weeklyLeaderboard[winner_name] = weeklyLeaderboard[winner_name] + 1
    else:        
        weeklyLeaderboard[winner_name] = 1
    return weeklyLeaderboard

# Saves weekly leaderboard to Pickle File
def saveWeeklyLeaderboard(weeklyLeaderboard):
    weeklyLeaderboardFileW = open("pickleFiles/weeklyLeaderboard", "wb")
    pickle.dump(weeklyLeaderboard, weeklyLeaderboardFileW)
    weeklyLeaderboardFileW.close()

# Takes a leaderboard, deletes anything with a zero value, then sorts it by its highest score
def formatLeaderBoard(leaderboard):
    topscores = ''
    sorted_list = ''
    sorted_dict = []

    leaderboard = {k: v for k, v in leaderboard.items() if v > 0}
            
    sorted_dict += sorted(leaderboard.items(), key=lambda kv: kv[1], reverse=True)
    for x in sorted_dict:
        sorted_list = [': '.join(map(str, x)) for x in sorted_dict]
    for y in sorted_list:
        topscores += str(y) + "\n"
    
    return topscores

### DATE MANAGEMENT METHODS ###

#Pulls the last week via Pickle File
def hasWeekChanged():
    curr_week = datetime.date.today().strftime("%V")
    most_recent_week = getRecentWeek()
    if (curr_week != most_recent_week):
        return True
    else:
        return False

#Pulls the last week via Pickle File
def getRecentWeek():
    openedFile = open('pickleFiles/weekTracker', 'rb')
    most_recent_week = pickle.load(openedFile)
    openedFile.close
    return most_recent_week

#Updates the weekTracker Pickle File
def updateWeek(week):
    openedFile = open('pickleFiles/weekTracker', 'wb')
    pickle.dump(week, openedFile)
    openedFile.close

### SLACK INTERACTION FUNCTIONS ###

# Pulls the slack results
def slackResult(messages):
    result = client.conversations_history(
        channel = conversation_id,
        inclusive=True,
        limit=messages
    )
    return result

# Returns slack text (to be used within a for loop)
def slackText(result, x):
    text = (result["messages"][x]["text"]).lower()
    return text
    
# Returns a Slack ID
def slackID(result, x):
    return result["messages"][x]["user"]

def printToSlack(string):
    client.chat_postMessage(channel=slackchannel, text=string)

# Reverse iterates through the guesses
def checkGuesses(wordKey, guessesChecked):
    result = slackResult(guessesChecked)
    for x in reversed(range(len(result['messages']))):
        guess = slackText(result, x)
        if (guess) in wordKey:
            userID = slackID(result, x)
            return True, userID, guess
    return False

def activateJumbleBot():

    # Checks if week has changed and if so, will 1. Update the current week, 2. Update the weekly leaderboard, 3. Reset the daily leaderboard
    if hasWeekChanged() == True:
        print("CONSOLE: Week Has Changed")

        current_week = datetime.date.today().strftime("%V")
        updateWeek(current_week)

        winner = calculateDailyLeaderboardWinner()
        weeklyLeaderboard = getWeeklyLeaderboard()
        weeklyLeaderboard = updateWeeklyLeaderboard(winner, weeklyLeaderboard)
        saveWeeklyLeaderboard(weeklyLeaderboard)

        resetDailyLeaderboard()
        printToSlack("A new week is here! \n\n The winner from last week is " + winner + "\n\nWeekly Leaderboard:\n\n" + formatLeaderBoard(weeklyLeaderboard))

    # Get the user dictionary which links unique IDs to players names. Get daily scores.
    userDic = getUserDictionary()
    dailyLeaderboard = getDailyLeaderboard()

    # Creates the words for the jumble
    easyKey = pickWords(3,6,5)
    mediumKey = pickWords(5,8,3)
    hardKey = pickWords(8,11,2)
    easyJumble = jumbleWords(easyKey)
    mediumJumble = jumbleWords(mediumKey)
    hardJumble = jumbleWords(hardKey)

    fullKey = easyKey + mediumKey + hardKey    
    textOutput = compileWords(easyJumble, mediumJumble, hardJumble)

    # Print Warning
    printToSlack("Jumble will start in 10 seconds.")
    time.sleep(10)

    # Print Jumble
    print(fullKey)
    printToSlack(textOutput)

    # Listen for scores. Respond when scores are inputted
    while len(fullKey) > 0:
        time.sleep(1)
        boolean = False

        # This logic runs if there's a correct guess in the last 5 messages. If there isn't, nothing happens. 
        boolean = checkGuesses(fullKey, 5)
        if boolean == False:
            "Do Nothing"

        else:
            boolean, userID, guess = checkGuesses(fullKey, 5)
            points = checkKey(guess, easyKey, mediumKey, hardKey)
            winner, userDic = findUserName(userDic, userID)
            updateDailyLeaderboard(winner, dailyLeaderboard, points)
            removeWords(guess, fullKey, easyJumble, easyKey, mediumJumble, mediumKey, hardJumble, hardKey)
            printToSlack(guess + " was correct! " + str(points) + " points for " + winner)
            checkJumbleReminder(fullKey, 6, 4, 2, easyJumble, mediumJumble, hardJumble)
            print("CONSOLE: Remaining words: " + str(fullKey))

    saveDailyLeaderboard(dailyLeaderboard)
    printToSlack("Daily Leaderboard:\n\n" + formatLeaderBoard(dailyLeaderboard))

activateJumbleBot()