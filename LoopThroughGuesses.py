from contextlib import nullcontext
from mimetypes import guess_all_extensions
from operator import truediv
import time
from unittest import result
import slack
from pathlib import Path
from dotenv import load_dotenv

instance = 'Barrytime'

# Below is the info required to run your BAT file as well as link to your Slack Instance (which must be approved via Slack APIs)
if instance == 'Barrytime':
    env_path = Path ('.')/'jumble(Barrytime).env'
    conversation_id = "xxx"
    SLACK_TOKEN = 'xxx'
    pointvalue = 0

load_dotenv(dotenv_path=env_path)
client = slack.WebClient(SLACK_TOKEN)

fullkey = ['guess0', 'guess4', 'Test9']

# Pulls the slack results
def SlackResult(messages):
    result = client.conversations_history(
        channel = conversation_id,
        inclusive=True,
        limit=messages
    )
    return result

# Returns slack text (to be used within a for loop)
def SlackText(result, x):
    text = (result["messages"][x]["text"]).lower()
    return text
    
# Returns a Slack ID
def SlackID(result):
    return result["messages"][0]["user"]

# Reverse iterates through the guesses
def checkGuesses(wordKey, guessesChecked):
    result = SlackResult(guessesChecked)
    for x in reversed(range(len(result['messages']))):
        guess = SlackText(result, x)
        if (guess) in wordKey:
            userID = SlackID(result)
            return True, userID, guess
    return False

# This is part of the primary "ActiveJumbleBot" function
boolean = checkGuesses(fullkey)
if boolean == False:
    print("no correct guess")

else:
    boolean, userID, guess = checkGuesses(fullkey)
    print(userID)
    print(guess)