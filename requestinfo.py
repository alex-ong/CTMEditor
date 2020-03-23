import re
from .util import LEAGUES

def removeNonNumber(input):
    result = re.sub("[^0-9]", "", input)
    return result



REPORT_PREFIX = ":redheart:"
SCHEDULE_PREFIX = ":fire:"

REPORT = 0
SCHEDULE = 1


# returns if there are multiple "fire" or "heart" emojis.
def isMultipleMessage(string):
    if string.count(REPORT_PREFIX) + string.count(SCHEDULE_PREFIX) > 1:
        return True

# use this to determine whether we want to actually do anything
# with the message.
def ReportingOrScheduling(string):
    if string.strip().startswith(REPORT_PREFIX):
        return REPORT
    if string.strip().startswith(SCHEDULE_PREFIX):
        return SCHEDULE
    else:
        return None


CC = ":cc:"
FC = ":fc:"
CT1 = ":ct::t1:"
CT2 = ":ct::t2:"
CT3 = ":ct::t3:"
CT = ":ct:"

LEAGUE_LIST = [CC, FC, CT1, CT2, CT3]


def safeInt(item):
    try:
        return int(item)
    except:
        return None

def findLeague(items):
    for i, item in enumerate(items):
        item = item.lower()
        if item == CC:
            return LEAGUES.CC
        elif item == FC:
            return LEAGUES.FC
        elif item == CT1:
            return LEAGUES.CT1
        elif item == CT2:
            return LEAGUES.CT2
        elif item == CT3:
            return LEAGUES.CT3
        elif item.lower == CT:
            nextIdx = i + 1
            # lbyl.  Not pythonic.
            if nextIdx < len(items):
                if items[nextIdx].contains("t1"):
                    return LEAGUES.CT1
                elif items[nextIdx].contains("t2"):
                    return LEAGUES.CT2
                elif items[nextIdx].contains("t3"):
                    return LEAGUES.CT3
    return None

def findMatchID(items):
    for i, item in enumerate(items):
        if item.lower() == "match" or item.lower() == "game":
            nextIdx = i + 1
            if nextIdx < len(items):
                numberOnly = removeNonNumber(
                    items[nextIdx]
                )  # convert "#20" to "20"
                result = safeInt(numberOnly)
                if result != 0:
                    return result
    return None

def findVOD(items):
    for item in items:
        if "twitch.tv" in item:
            return item
    return ""

class ReportInfo(object):
    def __init__(self, fullString):
        self.fullString = fullString
        items = fullString.split()
        self.matchID = findMatchID(items)
        self.league = findLeague(items)
        self.vod = findVOD(items)

        self.winner, self.winScore, self.loseScore = self.mapScores(items)

    # support Winner: playername (3-0)
    def mapScores(self, items):
        result = {}
        winnerIdx = None
        winner = None
        for idx, item in enumerate(items):
            item = item.lower()
            if item.startswith("winner") or item.startswith("winner:"):
                # next word is name
                winner = items[idx + 1]
                winnerIdx = idx + 1
                break

        # parse the score
        if not winner:
            return (None, 0, 0)

        if winner.endswith(")"):  # typo.  Kirby703(3-1)
            score = items[winnerIdx][-5:]
        elif items[winnerIdx + 1].startswith("("):  # Kirby703 (3-1)
            if len(items[winnerIdx + 1]) >= 4:
                score = items[winnerIdx + 1]
            else:
                score = ""
                idx = winnerIdx + 1
                while len(score) < 4:
                    idx += items[idx]
                    idx += 1
        elif (
            items[winnerIdx + 1][0] in "012345" and len(items[winnerIdx + 1]) == 3
        ):  # 3-1
            score = "(" + items[winnerIdx + 1] + ")"
        else:
            return (winner, None, None)

        # should have "(3-1)" now
        winnerScore = int(score[1])
        loserScore = int(score[3])
        return (winner, winnerScore, loserScore)

# :fire: I will restream :cc: match #20 @sundeco vs @DaAsiann at 6pm PDT (0100 UTC)
# :fire: I will restream :cc: match #20 @sundeco vs @DaAsiann on March 17 at 0700 PDT
class ScheduleInfo(object):
    def __init__(self, reporter, fullString):
        self.fullString = stringData
        self.reporter = reporter
        items = fullString.split()
        self.league = findLeague(items)
        self._time = None
    
    def mapTime(self):
        pass    