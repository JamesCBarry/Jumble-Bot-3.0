from urllib.request import Request, urlopen
import random
from random import shuffle
import slack

easyPoint = 0
mediumPoint = 0
hardPoint = 0

url = "https://raw.githubusercontent.com/openethereum/wordlist/master/res/wordlist.txt"
req = Request(url)
web_byte = urlopen(req).read()

webpage = web_byte.decode('utf-8')
fulllist = webpage.split("\n")

slackchannel = '#Riddles'

client = slack.WebClient("SLACK_TOKEN")

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
    if len(fullkey) == cutoff1 or cutoff2 or cutoff3:
        textOutput = "Remaining jumbles are: '\n\n'" + compileWords(easyJumble, mediumJumble, hardJumble)
        client.chat_postMessage(channel=slackchannel, text=textOutput)

# Returns what key the guess is in, along with the corresponding points
def checkKey(guess, easyKey, mediumKey, hardKey):
    if guess in easyKey:
        return easyKey, easyPoint
    elif guess in mediumKey:
        return mediumKey, mediumPoint
    elif guess in hardKey:
        return hardKey, hardPoint

# Removes jumbles from the full key, the specific key, and the jumble list
def removeWords(guess, currentKey, fullKey, easyJumble, easyKey, mediumJumble, mediumKey, hardJumble, hardKey):
    fullKey.remove(guess)
    if currentKey == easyKey:
        easyJumble.remove(easyJumble[easyKey.index(guess)])
        easyKey.remove(guess)
    if currentKey == mediumKey:
        mediumJumble.remove(mediumJumble[mediumKey.index(guess)])
        mediumKey.remove(guess)
    if currentKey == hardKey:
        hardJumble.remove(hardJumble[hardKey.index(guess)])
        hardKey.remove(guess)

easyKey = pickWords(3,6,5)
mediumKey = pickWords(6,8,3)
hardKey = pickWords(8,11,2)
easyJumble = jumbleWords(easyKey)
mediumJumble = jumbleWords(mediumKey)
hardJumble = jumbleWords(hardKey)

print(easyKey)
print(easyJumble)