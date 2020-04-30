import re
from .util import LEAGUES
from datetime import datetime, timedelta


def removeNonNumber(input):
    result = re.sub("[^0-9]", "", input)
    return result


REPORT_PREFIXES = ["<:redheart:545715946325540893>"]
REPORT_PREFIX = "<:redheart:545715946325540893>"

SCHEDULE_PREFIX = "🔥"
SCHEDULE_PREFIXES = ["🔥", ":fire:", ":flame:"]

REPORT = 0
SCHEDULE = 1


# returns if there are multiple "fire" or "heart" emojis.
def isMultipleMessage(string):
    number = 0
    for item in REPORT_PREFIXES:
        number += string.count(item)

    for item in SCHEDULE_PREFIXES:
        number += string.count(item)
    if number > 1:
        return True


# use this to determine whether we want to actually do anything
# with the message.
def ReportingOrScheduling(string):
    stripped = string.strip()
    if stripped.startswith(REPORT_PREFIX):
        return REPORT
    for item in SCHEDULE_PREFIXES:
        if stripped.startswith(item):
            return SCHEDULE
    else:
        return None


ME = "<:me:662518884057743391>"
CC = "<:cc:662518277091885066>"
FC = "<:fc:662518740159561738>"
T1 = "<:t1:688533378303131679>"
T2 = "<:t2:688533342563336271>"
T3 = "<:t3:688534577655972026>"
CT = "<:ct:688439996478259294>"

CT1 = CT + T1
CT2 = CT + T2
CT3 = CT + T3


LEAGUE_LIST = [CC, FC, CT1, CT2, CT3]


def safeInt(item):
    try:
        return int(item)
    except:
        return None


def safeIndex(items, search):
    if search in items:
        return items.index(search)
    return -1


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
        elif item == CT:
            nextIdx = i + 1
            # lbyl.  Not pythonic.
            if nextIdx < len(items):
                if "t1" in items[nextIdx]:
                    return LEAGUES.CT1
                elif "t2" in items[nextIdx]:
                    return LEAGUES.CT2
                elif "t3" in items[nextIdx]:
                    return LEAGUES.CT3
    return None


MATCH_WORDS = ["match", "game"]


def findMatchID(items):
    for i, item in enumerate(items):
        if item.lower() in MATCH_WORDS:
            nextIdx = i + 1
            if nextIdx < len(items):
                numberOnly = removeNonNumber(items[nextIdx])  # convert "#20" to "20"
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
        try:
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
        except IndexError:
            return (winner, None, None)

        # should have "(3-1)" now
        winnerScore = safeInt(score[1])
        loserScore = safeInt(score[3])
        return (winner, winnerScore, loserScore)


NOW = ["now", "shortly", "immediately", "soon", "momentarily"]
MYSELF = ["i", ":fire:i", "🔥i"]
# :fire: I will restream :cc: match #20 @sundeco vs @DaAsiann on Mar-17 at 0700 PDT
# :fire: I will restream :cc: match #20 @sundeco vs @DaAsiann at 0700 PDT
# :fire: Cancel :cc: match #20


class ScheduleInfo(object):
    def __init__(self, reporter, fullString):
        self.fullString = fullString

        items = fullString.lower().split()
        self.is_cancelled = self.checkCancel(items)
        self.league = findLeague(items)
        self.matchID = findMatchID(items)

        self.restreamer = self.findRestreamer(items, reporter)

    def checkCancel(self, items):
        cancel_idx = safeIndex(items, "cancel")
        if cancel_idx == 1:
            return True
        elif items[0].endswith("cancel"):  # ":fire:cancel"
            return True
        return False

    def findRestreamer(self, items, reporter):
        will_idx = safeIndex(items, "will")
        restream_idx = safeIndex(items, "restream")
        restreamer = reporter
        if will_idx != -1 and will_idx == restream_idx - 1:
            restreamer = items[will_idx - 1]
            if restreamer in MYSELF:
                restreamer = reporter
        return restreamer

    def mapNow(self):
        dt = datetime.utcnow()
        dateString = dt.strftime("%b-%d")
        timeString = dt.strftime("%H%M")
        timeZone = "UTC"
        return (dateString, timeString, timeZone)

    def mapRelative(self, amount, units):
        print("fucker", amount, units)
        print(units in ["hour", "hours"])
        dt = datetime.utcnow()
        if units in ["hour", "hours"]:
            dt = dt + timedelta(hours=float(amount))
        elif units in ["minute", "minutes"]:
            dt = dt + timedelta(minutes=float(amount))
        else:
            raise Exception("Couldn't find hours or minutes")

        dateString = dt.strftime("%b-%d")
        timeString = dt.strftime("%H%M")
        timeZone = "UTC"
        return (dateString, timeString, timeZone)

    def mapTime(self):
        dateString = None
        timeString = None
        timeZone = None

        items = self.fullString.lower().split()

        # right now.  Shortly, immediately, now
        for string in NOW:
            if string in items:
                print("now")
                return self.mapNow()

        # relative time: in 90 minutes
        inIndex = safeIndex(items, "in")  # restreaming in 5 hours etc.
        if inIndex != -1:
            print("in x hours")
            return self.mapRelative(items[inIndex + 1], items[inIndex + 2])

        # exact date: on mar-30 at 1300 UTC
        onIndex = safeIndex(items, "on")
        atIndex = safeIndex(items, "at")
        print(onIndex, atIndex)
        try:
            if onIndex != -1:
                dateString = items[onIndex + 1]
            if atIndex != -1:
                timeString = items[atIndex + 1]
                timeZone = items[atIndex + 2]
        except:
            pass

        return (dateString, timeString, timeZone)
