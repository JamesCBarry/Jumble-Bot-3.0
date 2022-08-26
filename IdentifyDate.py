import datetime
import pickle

most_recent_week = str(29)

#Checks if week has changed. Returns True or False
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