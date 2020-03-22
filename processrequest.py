from .reportinfo import ReportingOrScheduling, ReportInfo, REPORT
from .matchinfo import ConvertToMatches, GetMatchByIndex, GetValidMatches
from .spreadsheetdata import loadSpreadsheetData
from .playermatch import matchPlayers
from .util import leagueString
from .channelcache import ChannelSummaryCache, GetSummarySettings, SaveSummarySettings
from .channelsummary import GenerateChannelMessages

#try:
from ..discord import get_channel
#except:
#    def get_channel():
#        return None
#
    
def processRequest(string):
    msgType = ReportingOrScheduling(string)
    if msgType == REPORT:
        r = ReportInfo(string)
        print ("Reading League", leagueString(r.league))
        success, message = processReport(r) 
        # return what league we read as well as the result of processing the report
        if success:
            return (r.league, message)
        else:
            return (None, message)

# return success and message
def processReport(r):    
    if r.league is None:        
        return (False, "Could not find league\n")
    if r.matchID is None:            
        return (False, "Could not find match id\n")
    sheet, matchData, playerList = loadSpreadsheetData(leagueString(r.league))
    matches = ConvertToMatches(matchData)
    m = GetMatchByIndex(matches, r.matchID)

    result = ""
    if m is None or not m.isValidMatch(playerList):
        result += "Could not find match id:" + str(r.matchID) + "\n"
        result += "Try one of these matches:\n"       
        valids = GetValidMatches(matches, playerList)        
        result += "\n".join(str(item) for item in valids)
        return (False, result)
    
    if (m.matchFinished):
        result +=  ("Warning, match already reported... " + str(m) + "\n")
    
    print ("Trying to match " + r.winner + " to " + m.player1 + " or " + m.player2)
    which = matchPlayers(r.winner,m.player1,m.player2)
    if which is None:
        result += ("Could not match " + r.winner + " to either : " + m.player1 + " or "  + m.player2 + "\n")
        return (False, result)
    elif which == "P1":
        print("Matched " + r.winner + " to " + m.player1 + "\n")
        m.writeMatchInfo(r.winScore,r.loseScore,sheet)
    elif which == "P2":
        result += ("Matched " + r.winner + " to " + m.player2 + "\n")
        m.writeMatchInfo(r.loseScore,r.winScore,sheet)
    
    #finally, push result to cloud    
    result += "Successfully logged result\n"

    return (True, result)

# expects "cc", "fc" etc.
def updateChannel(context, league):
    channelSettings = GetSummarySettings()[league]
    
    for messageID in channelSettings.messages:
        message = context.fetch_message(channelSettings.channelID, messageID)
        if message is not None:        
            context.delete_message(message)
        

    newMessages = GenerateChannelMessages(league)
    channelSettings.messages = []
    for string in newMessages:
        message = context.send_message(string)
        channelSettings.messages.append(message.id)
    SaveSummarySettings()
    

def setupChannel(context, league):
    print(context.channel.id)
    channelSettings = GetSummarySettings()[league]
    channelSettings.channelID = context.channel.id
    SaveSummarySettings()
    
    updateChannel(context, league)
    # delete requestors message
    context.delete_message(context.message)

if __name__ == '__main__':
    TEST_STRING = (":redheart: Completed :cc: Match 13 (XeaL337 vs VideoGamesBrosYT) - Winner: Video 3-0\n"+
                   "VOD: https://www.twitch.tv/videos/569198637")
    result = processRequest(TEST_STRING)
    print(result)
    