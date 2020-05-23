from .matchinfo import ConvertToMatches, GetMatchByIndex, ValidMatchesString
from .spreadsheetdata import loadLeagueData
from .playermatch import matchPlayers
from .requestinfo import LEAGUE_LIST, LEAGUE_LIST_PP
from .util import leagueString

EXAMPLE_MSG = ":redheart: :cc: Completed Match 3 (name_no_space vs name2) Winner: name_no_space (3-1)\n"
# return whether we succeeded, as well as error message
def processReport(r):
    if r.league is None:
        return (
            False,
            "Could not find league\n Please include one of these: "
            + " ".join(LEAGUE_LIST_PP)
            + "\n"
            + EXAMPLE_MSG,
        )

    sheet, matchData, player_data, _ = loadLeagueData(leagueString(r.league))
    playerList = [player[0].value for player in player_data]
    matches = ConvertToMatches(matchData)

    if r.matchID is None:
        result = (
            "Could not find match id\n Make sure you wrote match # with a space.\n"
            + EXAMPLE_MSG
        )
        result += ValidMatchesString(matches, playerList)
        return (False, result)

    m = GetMatchByIndex(matches, r.matchID)

    result = ""
    if m is None:
        result += "Could not find match id:" + str(r.matchID) + "\n"
        result += "Try one of these matches:\n"
        result += ValidMatchesString(matches, playerList)
        return (False, result)

    if not m.isValidMatch(playerList):
        result += "Match can't be played yet: Match " + str(r.matchID) + "\n"
        result += str(m) + "\n"
        return (False, result)

    if r.winner is None:
        result = 'Could not find winner.\n Please use "winner:" tag\n'
        result += "Valid players: " + m.player1 + " or " + m.player2 + "\n"
        result += EXAMPLE_MSG
        return (False, result)

    if r.winScore is None:
        result = "Could not find score.\n Please put score as (3-x) straight after winner name\n"
        result += EXAMPLE_MSG
        return (False, result)

    if r.loseScore is None:
        result = "Could not find loser's score.\n Please put score as (3-x) straight after winner name\n"
        result += EXAMPLE_MSG
        return (False, result)

    if m.matchFinished:
        result += "Warning, match already reported... " + str(m) + "\n"

    result += (
        "Reporting for " + leagueString(r.league) + " Match " + str(r.matchID) + "\n"
    )
    which = matchPlayers(r.winner, m.player1, m.player2)
    if which is None:
        result += (
            "Could not match "
            + r.winner
            + " to either : "
            + m.player1
            + " or "
            + m.player2
            + "\n"
        )
        return (False, result)
    elif which == "P1":
        result += (
            "Matched "
            + r.winner
            + " to "
            + m.player1
            + ", Score ("
            + str(r.winScore)
            + "-"
            + str(r.loseScore)
            + ")\n"
        )
        m.writeMatchInfo(r.winScore, r.loseScore, r.vod, sheet)
    elif which == "P2":
        result += (
            "Matched "
            + r.winner
            + " to "
            + m.player2
            + ", Score ("
            + str(r.winScore)
            + "-"
            + str(r.loseScore)
            + ")\n"
        )
        m.writeMatchInfo(r.loseScore, r.winScore, r.vod, sheet)
    # finally, push result to cloud
    result += "Successfully logged result\n"

    return (True, result)
