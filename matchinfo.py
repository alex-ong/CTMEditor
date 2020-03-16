def isMatch(data):
    value = data[0].intValue 
    return  value >= 1
    
class MatchInfo(object):
    def __init__(self, data):        
        self.matchNo = data[0].intValue
        self.player1 = data[1].strValue
        self.score1 = data[2].intValue
        self.score2 = data[3].intValue
        self.player2 = data[4].strValue
        self.winner = data[5].strValue
        self.loser = data[6].strValue
        self.matchFinished = self.score1 != 0 or self.score2 != 0
        self.matchTime = data[7].strValue
        self.restreamer = data[8].strValue
        self._isValidMatch = None
        self.data = data
        
    def isValidMatch(self, playerList):
        if self._isValidMatch is None:
            self._isValidMatch = (self.player1 in playerList and 
                                  self.player2 in playerList)
                                  
        return self._isValidMatch
    
    # writes match info to data backing, but does not commit over internet
    def writeMatchInfo(self, player1Score, player2Score):
        self.data[2].SetValue(player1Score)
        self.data[3].SetValue(player2Score)

# returns a list of MatchInfo
def ConvertToMatches(fullData):
    result = []
    for line in fullData:
        if isMatch(line):
            m = MatchInfo(line)
            result.append(m)
    return result
# given a list of Matches, returns unplayed matches that have 
# players on both sides.
def GetValidMatches(matches):
    result = [m in matches if m.isValidMatch()]
    return result

# given a match index and a list of matches, returns 
# the correct MatchInfo.
def GetMatchIndex(matches, index):
    for m in matches:
        if m.matchNo == index:
            return m
    return None
    