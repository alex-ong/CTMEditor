def safeInt(value):
    if value == '':
        return None
    try:
        return int(value)
    except:
        return None

class MatchInfo(object):
    @staticmethod
    def isValidMatchID(rowOfCells):
        value = int(rowOfCells[0].value)
        return  value >= 1
    
    def __init__(self, data):        
        self.matchNo = int(data[0].value)
        self.player1 = data[1].value
        self.score1 = safeInt(data[2].value)
        self.score2 = safeInt(data[3].value)
        self.player2 = data[4].value
        self.winner = data[5].value
        self.loser = data[6].value
        self.matchFinished = ((self.score1 is not None and self.score2 is not None) and
                              (self.score1 > 0 or self.score2 > 0))
        self.matchTime = data[7].value
        self.restreamer = data[8].value
        self._isValidMatch = None
        self.data = data
        
    def isValidMatch(self, playerList):
        if self._isValidMatch is None:
            self._isValidMatch = (self.player1 in playerList and
                                  self.player2 in playerList)

        return self._isValidMatch
    
    # writes match info to data backing, but does not commit over internet
    def writeMatchInfo(self, player1Score, player2Score, wksheet):
        if (player1Score <= 0 and player2Score <= 0):            
            player1Score = ""
            player2Score = ""
        wksheet.update_cell(self.data[2].row,self.data[2].col, player1Score)
        wksheet.update_cell(self.data[3].row,self.data[3].col, player2Score)
    
    def __str__(self):
        if self.matchFinished:
            return (str(self.matchNo) + ": " + self.player1 + " (" + str(self.score1) + "-" + 
                    str(self.score2) + ") " + self.player2)
        
        vm = ""
        if self._isValidMatch is not None:
            if self._isValidMatch:
                vm = "(playable)"
            else:
                vm = "(not playable)"
        return (str(self.matchNo) + ": " + self.player1 + " vs " + self.player2 + " " + vm)

def SplitDatabaseRows(fullData):
    if len(fullData) == 0:
        return []
    currentRowIdx = None
    currentRow = []
    result = []
    for item in fullData:        
        if item.row != currentRowIdx:
            if currentRowIdx is not None:
                result.append(currentRow)
            currentRow = [item]
            currentRowIdx = item.row
        else:
            currentRow.append(item)
    if len(currentRow) > 0:
        result.append(currentRow)

    return result
            
        
# returns a list of MatchInfo
def ConvertToMatches(fullData):
    rows = SplitDatabaseRows(fullData)   
    result = []
    for row in rows:
        if MatchInfo.isValidMatchID(row):
            m = MatchInfo(row)
            result.append(m)
    return result
    
# given a list of Matches, returns unplayed matches that have
# players on both sides.
def GetValidMatches(matches, playerlist):
    result = [m for m in matches if m.isValidMatch(playerlist) and not m.matchFinished]
    return result

# given a match index and a list of matches, returns
# the correct MatchInfo.
def GetMatchByIndex(matches, index):
    for m in matches:
        if m.matchNo == index:
            return m
    return None