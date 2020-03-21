from .reportinfo import ReportingOrScheduling, ReportInfo, REPORT
from .matchinfo import ConvertToMatches, GetMatchByIndex
from .spreadsheetdata import loadSpreadsheetData
from .playermatch import matchPlayers

def processRequest(string):
    msgType = ReportingOrScheduling(string)
    if msgType == REPORT:
        r = ReportInfo(string)
        print ("Reading League", r.league)
        return processReport(r)

def processReport(r):    
    if r.league is None:        
        return "Could not find league\n"
    if r.matchID is None:            
        return "Could not find match id\n"
    sheet, ssData = loadSpreadsheetData(r.league)    
    matches = ConvertToMatches(ssData)
    m = GetMatchByIndex(matches, r.matchID)
    if m is None:
        return "Could not find match id" + str(r.matchID)

    result = ""
    if (m.matchFinished):
        result +=  ("Warning, match already reported... " + str(m) + "\n")
    
    print ("Trying to match " + r.winner + " to " + m.player1 + " or " + m.player2)
    which = matchPlayers(r.winner,m.player1,m.player2)
    if which is None:
        result += ("Could not match " + r.winner + " to either : " + m.player1 + " or "  + m.player2 + "\n")
        return result
    elif which == "P1":
        print("Matched " + r.winner + " to " + m.player1 + "\n")
        m.writeMatchInfo(r.winScore,r.loseScore,sheet)
    elif which == "P2":
        result += ("Matched " + r.winner + " to " + m.player2 + "\n")
        m.writeMatchInfo(r.loseScore,r.winScore,sheet)
    
    #finally, push result to cloud    
    result += "Successfully logged result\n"
    return result
        
    
    
        
        
if __name__ == '__main__':
    TEST_STRING = (":redheart: Completed :cc: Match 13 (XeaL337 vs VideoGamesBrosYT) - Winner: Video 3-0\n"+
                   "VOD: https://www.twitch.tv/videos/569198637")
    result = processRequest(TEST_STRING)
    print(result)
    