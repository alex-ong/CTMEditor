from reportinfo import ReportingOrScheduling, ReportInfo, REPORT
import matchinfo
import leagueData
import spreadsheetData 

def processRequest(string, user):
    msgType = reportinfo.ReportingOrScheduling(string)
    if msgType == REPORT:
        r = ReportInfo(string)
        return processReport(r)
def processReport(r):    
    if r.league is None:        
        return "Could not find league"
    if r.matchID is None:            
        return "Could not find match id"
    ssData = spreadsheetData.downloadLeague(r.league)
    matches = matchinfo.ConvertToMatches(ssData)
    
    matchinfo.GetMatchByIndex(r.matchID)
    
            
        
        
        