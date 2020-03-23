from .matchinfo import ConvertToMatches, GetMatchByIndex, ValidMatchesString
from .spreadsheetdata import loadSpreadsheetData
from .util import leagueString
import pytz

# return whether we succeeded, as well as error message
def processSchedule(s):
    if s.league is None:
        return (
            False,
            "Could not find league\n Please include one of these: "
            + " ".join(LEAGUE_LIST)
            + "\n",
        )

    sheet, matchData, playerList = loadSpreadsheetData(leagueString(s.league))
    matches = ConvertToMatches(matchData)

    if s.matchID is None:
        result = (
            "Could not find match id\n Make sure it you wrote match # with a space.\n"
        )
        result += ValidMatchesString(matches, playerList)
        return (False, result)

    m = GetMatchByIndex(matches, s.matchID)

    result = ""
    if m is None:
        result += "Could not find match id:" + str(s.matchID) + "\n"
        result += "Try one of these matches:\n"
        result += ValidMatchesString(matches, playerList)
        return (False, result)

    if not m.isValidMatch(playerList):
        result += "Warning: match can't be played yet: " + str(s.matchID) + "\n"
        result += str(m) + "\n"
        result += "Don't worry, i'll still schedule it.\n"
        return (False, result)

    result += (
        "Attempting scheduling for "
        + leagueString(s.league)
        + " Match "
        + str(s.matchID)
        + "\n"
    )

    date, time, tz = s.mapTime()

    result += "Date: " + str(date) + " Time: " + str(time) + "Timezone: " + str(tz)

    result += "Restreamer: " + str(s.restreamer)
    # on success, write back to the spreadsheet lmao.
    # m.writeRestreamInfo(timestampstring, restreamerstring)
    return (False, result)
