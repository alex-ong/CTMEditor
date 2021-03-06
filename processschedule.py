from .matchinfo import ConvertToMatches, GetMatchByIndex, ValidMatchesString
from .spreadsheetdata import loadLeagueData
from .util import leagueString, leagueEmoteMD
from .requestinfo import LEAGUE_LIST, LEAGUE_LIST_PP


EXAMPLE_MSG = (
    ":fire: username will restream :cc: Match 5 (this_is vs ignored) on apr-01 at hhmm UTC\n"
    + ":fire: i        will restream :cc: Match 5 now\n"
    + ":fire: i        will restream :cc: Match 5 in 35 minutes\n"
    ":fire: Cancel :cc: Match 5\n"
)

# return whether we succeeded, as well as error message
def processSchedule(s):
    if s.league is None:
        return (
            False,
            "Could not find league\n Please include one of these: "
            + " ".join(LEAGUE_LIST_PP)
            + "\n"
            + EXAMPLE_MSG
            + "\n",
        )

    sheet, matchData, player_data, _ = loadLeagueData(leagueString(s.league))
    playerList = [player[0].value for player in player_data]
    matches = ConvertToMatches(matchData)

    if s.matchID is None:
        result = (
            "Could not find match id\n Make sure you wrote match # with a space.\n"
            + EXAMPLE_MSG
            + "\n",
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
        result += (
            "Warning: match can't be played yet: Match "
            + str(s.matchID)
            + "("
            + str(m)
            + ")\n"
        )
        result += "Don't worry, i'll still try to schedule it.\n"

    else:
        result += (
            "Attempting scheduling for "
            + leagueString(s.league)
            + " Match "
            + str(s.matchID)
            + "\n"
        )

    if s.is_cancelled:
        result += "Cancelled match."
        m.writeRestreamInfo("", "", sheet)
        return (True, result)

    date, time, tz = s.mapTime()

    result += (
        "Date: " + str(date) + " Time: " + str(time) + " Timezone: " + str(tz) + "\n"
    )
    if tz is None:
        result += "Sorry, no timezone detected, Try: [ on MAR-04 at 0700 EST ] or [now] or [in 90 minutes]"
        return (False, result)
    if time is None:
        result += "Sorry, no time detected. Try: [ on MAR-04 at 0700 EST ] or [now] or [in 90 minutes]"
        return (False, result)
    if date is None:
        result += "Sorry, no date detected. Try: [ on MAR-04 at 0700 EST ] or [now] or [in 90 minutes]"
        return (False, result)

    # now to fix the goddamn time.
    # todo, fix and change to UTC. good luck future alex.

    result += "Restreamer: " + str(s.restreamer) + "\n"
    # on success, write back to the spreadsheet lmao.
    timestampstring = " ".join(str(item) for item in [date, time, tz])

    old_r, old_t = m.writeRestreamInfo(timestampstring, s.restreamer, sheet)
    old_r = "".join(old_r.split())
    if old_r and old_t:
        result += "```\n```diff\n"
        result += "- Warning, overridding existing schedule:\n"
        result += f"Restreamer: {old_r} | Time: {old_t}\n"
        result += "- If this is not your intention, copy paste this message to undo:\n"
        date, time, tz = old_t.split()
        league_md = leagueEmoteMD(s.league)
        result += f":fire: {old_r} will restream {league_md} Match {s.matchID} on {date} at {time} {tz}\n"
    result += "Successfully updated.\n"
    return (True, result)
