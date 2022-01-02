def safeInt(value):
    if value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


class MatchInfo(object):
    @staticmethod
    def isValidMatchID(rowOfCells):
        value = int(rowOfCells[0].value)
        return value >= 1

    def __init__(self, data):
        self.matchNo = safeInt(data[0].value)
        self.player1 = data[1].value
        self.score1 = safeInt(data[2].value)
        self.score2 = safeInt(data[3].value)
        self.player2 = data[4].value
        self.winner = data[5].value
        self.loser = data[6].value
        self.matchFinished = (self.score1 is not None and self.score2 is not None) and (
            self.score1 > 0 or self.score2 > 0
        )
        self.matchTime = data[7].value
        self.restreamer = data[8].value
        self.vod = data[9].value
        self._isValidMatch = None
        self.data = data

    def printableScore(self):
        if not self.matchFinished:
            return ""
        s1 = str(self.score1) if self.score1 is not None else "*"
        s2 = str(self.score2) if self.score2 is not None else "*"
        return s1 + "-" + s2

    def isValidMatch(self, playerList):
        if self.matchNo is None:
            return False
        if self._isValidMatch is None:
            self._isValidMatch = (
                self.player1 in playerList and self.player2 in playerList
            )

        return self._isValidMatch

    # writes match info to data backing, but does not commit over internet
    def writeMatchInfo(self, player1Score, player2Score, vod, wksheet, matchTimeStamp, reporter):
        writeMatchTime = False
        if player1Score <= 0 and player2Score <= 0:
            player1Score = ""
            player2Score = ""
        elif not self.matchTime or len(self.matchTime) == 0:
            matchTimeStamp = matchTimeStamp
            restreamer = reporter
            writeMatchTime = True
            
        wksheet.update_cell(self.data[2].row, self.data[2].col, player1Score)
        wksheet.update_cell(self.data[3].row, self.data[3].col, player2Score)
        wksheet.update_cell(self.data[9].row, self.data[9].col, vod)
        
        if writeMatchTime:
            wksheet.update_cell(self.data[7].row, self.data[7].col, matchTimeStamp)
            wksheet.update_cell(self.data[8].row, self.data[8].col, restreamer)
        
    def writeRestreamInfo(self, matchTimeStamp, restreamer, wksheet):
        old_r, old_time = self.restreamer, self.matchTime
        wksheet.update_cell(self.data[7].row, self.data[7].col, matchTimeStamp)
        wksheet.update_cell(self.data[8].row, self.data[8].col, restreamer)
        return old_r, old_time

    def __str__(self):
        if self.matchFinished:
            return (
                str(self.matchNo)
                + ": "
                + self.player1
                + " ("
                + str(self.score1)
                + "-"
                + str(self.score2)
                + ") "
                + self.player2
            )

        vm = ""
        if self._isValidMatch is not None:
            if self._isValidMatch:
                vm = "(playable)"
            else:
                vm = "(not playable)"
        return (
            str(self.matchNo) + ": " + self.player1 + " vs " + self.player2 + " " + vm
        )


# returns a list of MatchInfo
def ConvertToMatches(rows):
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


def ValidMatchesString(matches, playerList):
    valids = GetValidMatches(matches, playerList)
    result = "\n".join(str(item) for item in valids) + "\n"
    return result


# given a match index and a list of matches, returns
# the correct MatchInfo.
def GetMatchByIndex(matches, index):
    for m in matches:
        if m.matchNo == index:
            return m
    return None
