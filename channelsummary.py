from .spreadsheetdata import loadSpreadsheetData
from .matchinfo import ConvertToMatches, GetValidMatches
def GenerateChannelMessages(league):
    result = []
    
    result.append(GenerateUnplayedMatches(league))
    result.append("message 2.")
    result.append("message 3.")
        
    return result

def tabulate(items):
    return "| " + " | ".join(items) + " |\n"

def GenerateUnplayedMatches(league):
    sheet, game_data, player_names = loadSpreadsheetData(league)
    matches = ConvertToMatches(game_data)
    matches = GetValidMatches(matches, player_names)
    result = "Playable Matches: \n"
    result += "```\n"            
    title = [ "M#", "Player1".ljust(15), "Player2".ljust(15)]    
    result += tabulate(title)
    result += "-" * len(tabulate(title)-1) + "\n"
    for match in matches:
        line = [str(match.matchNo).rjust(2),
                str(match.player1).ljust(15),
                str(match.player2).ljust(15)]
        result += tabulate(line) 
    result += "```\n"
    return result