from .matchinfo import ConvertToMatches, GetMatchByIndex, ValidMatchesString
from .spreadsheetdata import loadSpreadsheetData
from .util import leagueString
from .requestinfo import LEAGUE_LIST
import pytz

EXAMPLE_MSG = ":fire: i/username will restream :cc: Match 5 (this_is vs ignored) on apr-01 at hhmm UTC"

# return whether we succeeded, as well as error message
def processSchedule(s):
    if s.league is None:
        return (
            False,
            "Could not find league\n Please include one of these: "
            + " ".join(LEAGUE_LIST) + "\n"
            + EXAMPLE_MSG + "\n",
        )

    sheet, matchData, playerList, _ = loadSpreadsheetData(leagueString(s.league))
    matches = ConvertToMatches(matchData)

    if s.matchID is None:
        result = (
            "Could not find match id\n Make sure you wrote match # with a space.\n"
            + EXAMPLE_MSG + "\n",
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
        result += "Warning: match can't be played yet: Match " + str(s.matchID) + "(" + str(m) + ")\n"
        result += "Don't worry, i'll still try to schedule it.\n"

    else:
        result += (
            "Attempting scheduling for "
            + leagueString(s.league)
            + " Match "
            + str(s.matchID)
            + "\n"
        )

    date, time, tz = s.mapTime()

    result += "Date: " + str(date) + " Time: " + str(time) + " Timezone: " + str(tz) + "\n"
    if tz is None:
        result += "Sorry, no timezone detected, Try: [ on MAR-04 at 0700 EST ]"
        return (False, result)
    if time is None:
        result += "Sorry, no time detected. Try: [ on MAR-04 at 0700 EST ]"
        return (False, result)
    if date is None:
        result += "Sorry, no date detected. Try: [ on MAR-04 at 0700 EST ]"
        return (False, result)
    
    # now to fix the goddamn time.
    # todo, fix and change to UTC. good luck future alex.

    result += "Restreamer: " + str(s.restreamer) + "\n"
    # on success, write back to the spreadsheet lmao.
    timestampstring = " ".join(str(item) for item in [date,time,tz])

    m.writeRestreamInfo(timestampstring, s.restreamer, sheet)
    result += "Successfully updated.\n"
    return (True, result)
