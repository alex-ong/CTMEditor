
#returns if there are multiple "fire" or "heart" emojis.
def isMultipleMessage(string):
    pass
    
#splits multiple reports into seperate strings.
def SplitMultipleMessages(string):
    result = []
    return result    

REPORT_PREFIX = ":heart:"
SCHEDULE_PREFIX = ":fire:"
    
REPORT = 0
SCHEDULE = 1    

def ReportingOrScheduling(string):
    if string.strip().startswith(REPORT_PREFIX):
        return REPORT
    if string.strip().startswith(SCHEDULE_PREFIX):
        return SCHEDULE
    
CC = ":cc:"
FC = ":fc:"
CT1 = ":ct::t1:"
CT2 = ":ct::t2:"
CT = ":ct:"

def safeInt(item):
    try:
       return int(item)
    except:
       return 0
class ReportingString(object):
    def __init__(self, fullString):
        self.fullString = fullString
        items = fullString.split()
        self.matchID = self.findMatchID(items)
        self.players = self.findPlayers(items)
        self.score = self.findScore(items)
        self.league = self.findLeague(items)
        winner = self.findWinner(items)
    
    def findMatchID(self, items):        
        for i, item in items.enumerate:            
            if item.lower == "match":
                nextIdx = i + 1                
                if nextIdx < len(items):
                    result = safeInt(items[nextIdx])
                    if result != 0:
                        return result
        return 0
        
    def findLeague(self,items):
        for i, item in enumerate(items):
            if item.lower == CC:
                return 'cc'
            elif item.lower == FC:
                return 'fc'
            elif item.lower == CT1:
                return 'ct1'
            elif item.lower == CT2:
                return 'ct2'
            elif item.lower == CT:
                nextIdx = i+1
                #lbyl. Not pythonic.
                if nextIdx < len(items):
                    if items[nextIdx].contains('t1'):
                        return 'ct1'
                    elif items[nextIdx].contains('t2'):
                        return 'ct2'
        return ''
        
    #support three formats.
    # a vs b
    # a vs. b
    # a def. b
    # a def b
    # a > b
    # hard: a (3 - 0) b    
    def findPlayers(self, items):
        for i, item in enumerate(items):
            if item in ['vs', 'vs.','def','def.','>']:
                return (items[i-1],items[i+1])
        return []
    
    #support (3-0)
    #hard: support (3) playerb(2)
    def findScore(self, items):
        pass
        
    def findVOD(self, items):
        for item in items:
            if item.contains("twitch.tv"):
                return item
        return ""
        
    
class SchedulingString(object):
    def __init__(self):
        pass
