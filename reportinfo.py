import re
def removeNonNumber(input):
    result = re.sub("[^0-9]", "", input)
    return result

#returns if there are multiple "fire" or "heart" emojis.
def isMultipleMessage(string):
    pass
    
#splits multiple reports into seperate strings.
def SplitMultipleMessages(string):
    result = []
    return result    

REPORT_PREFIX = ":redheart:"
SCHEDULE_PREFIX = ":fire:"
    
REPORT = 0
SCHEDULE = 1    

# use this to determine whether we want to actually do anything
# with the message.
def ReportingOrScheduling(string):
    if string.strip().startswith(REPORT_PREFIX):
        return REPORT
    if string.strip().startswith(SCHEDULE_PREFIX):
        return SCHEDULE
    else:
        return None
    
CC = ":cc:"
FC = ":fc:"
CT1 = ":ct::t1:"
CT2 = ":ct::t2:"
CT = ":ct:"

def safeInt(item):
    try:
       return int(item)
    except:
       return None
       
class ReportInfo(object):
    def __init__(self, fullString):
        self.fullString = fullString
        items = fullString.split()
        self.matchID = self.findMatchID(items)
        self.league = self.findLeague(items)
        self.vod = self.findVOD(items)
        self.winner, self.winScore, self.loseScore = self.mapScores(items) 
    
    def findMatchID(self, items):
        for i, item in enumerate(items):
            if item.lower() == "match":
                nextIdx = i + 1
                if nextIdx < len(items):
                    numberOnly = removeNonNumber(items[nextIdx]) #convert "#20" to "20"
                    result = safeInt(numberOnly)
                    if result != 0:
                        return result
        return None
        
    def findLeague(self,items):
        for i, item in enumerate(items):
            item = item.lower()
            if item == CC:
                return 'cc'
            elif item == FC:
                return 'fc'
            elif item == CT1:
                return 'ct1'
            elif item == CT2:
                return 'ct2'
            elif item.lower == CT:
                nextIdx = i + 1
                #lbyl.  Not pythonic.
                if nextIdx < len(items):
                    if items[nextIdx].contains('t1'):
                        return 'ct1'
                    elif items[nextIdx].contains('t2'):
                        return 'ct2'
        return None
        
    
    
    #support Winner: playername (3-0)
    def mapScores(self, items):
        result = {}
        winnerIdx = None
        winner = None
        for idx, item in enumerate(items):
            item = item.lower()            
            if item.startswith("winner") or item.startswith("winner:"):
                #next word is name
                winner = items[idx + 1]
                winnerIdx = idx + 1
                break
        
        #parse the score
        if not winner:
            return ("Couldnt find winner. Make sure you have 'Winner:' in your message")
        if winner.endswith(')'): #typo.  Kirby703(3-1)
            score = items[winnerIdx][-5:]
        elif items[winnerIdx + 1].startswith('('): #Kirby703 (3-1)
            if len(items[winnerIdx + 1]) >= 4:
                score = items[winnerIdx + 1]
            else:
                score = ""
                idx = winnerIdx + 1
                while len(score) < 4:
                    idx += items[idx]
                    idx += 1
        elif items[winnerIdx + 1][0] in '12345' and len(items[winnerIdx + 1]) == 3: #3-1
            score = "(" + items[winnerIdx + 1] + ")"
        #should have "(3-1)" now
        winnerScore = int(score[1])
        loserScore = int(score[3])
        return (winner, winnerScore, loserScore)
                
    def findVOD(self, items):
        for item in items:
            if "twitch.tv" in item:
                return item
        return ""
        
    
class SchedulingInfo(object):
    def __init__(self,stringData):
        pass

            