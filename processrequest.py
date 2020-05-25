from .requestinfo import (
    ReportingOrScheduling,
    ReportInfo,
    ScheduleInfo,
    REPORT,
    SCHEDULE,
    isMultipleMessage,
)
from .util import leagueString
from .channelcache import GetSummarySettings, SaveSummarySettings
from .channelsummary import GenerateChannelMessages
from .processreport import processReport
from .processschedule import processSchedule

import discord as discordpy
import threading

LOCK = None
if LOCK is None:
    LOCK = threading.RLock()

# split between report or schdule and call appropriate side.
def processRequest(user, string):
    msgType = ReportingOrScheduling(string)
    if msgType != REPORT and msgType != SCHEDULE:
        return (None, "Couldn't find :fire: or :redheart:")
    if isMultipleMessage(string):
        return (
            None,
            "You have multiple :fire: or :redheart: in your message! Only one report per message!",
        )

    if msgType == REPORT:
        data = ReportInfo(user, string)
        success, message = processReport(data)
    elif msgType == SCHEDULE:
        data = ScheduleInfo(user, string)
        success, message = processSchedule(data)

    if success:
        return (leagueString(data.league), message)
    else:
        return (None, message)


# expects "cc", "fc" etc.
def updateChannel(context, league, usernameLookup=None):
    global LOCK
    try:
        LOCK.acquire()
        channelSettings = GetSummarySettings()[league]

        for messageID in channelSettings.messages:
            try:
                message = context.fetch_message(channelSettings.channelID, messageID)
                if message is not None:
                    context.delete_message(message)
            except:
                print("Message not found: " + str(messageID))
        newMessages = GenerateChannelMessages(league, usernameLookup)
        channelSettings.messages = []
        for string in newMessages:
            if isinstance(string, discordpy.File):
                message = context.send_message_full(
                    channelSettings.channelID, file=string
                )
            else:
                message = context.send_message_full(channelSettings.channelID, string)
            channelSettings.messages.append(message.id)
        SaveSummarySettings()
    finally:
        LOCK.release()


# returns true if we posted a message in the reporting channel.
def checkChannelPeon(context):
    global LOCK
    try:
        LOCK.acquire()
        channelSettings = GetSummarySettings()["reporting"]
        return context.channel.id == channelSettings.channelID
    finally:
        LOCK.release()


# call this to save which channel to write our results to.
def setupChannel(context, league, usernameLookup):
    global LOCK
    try:
        LOCK.acquire()
        channelSettings = GetSummarySettings()[league]
        channelSettings.channelID = context.channel.id
        SaveSummarySettings()
        if league == "reporting":
            context.send_message("This is now the channel where match reports are due.")
            return
        updateChannel(context, league, usernameLookup)
        # delete requestors message
        context.delete_message(context.message)
    finally:
        LOCK.release()


if __name__ == "__main__":
    TEST_STRING = (
        ":redheart: Completed :cc: Match 13 (XeaL337 vs VideoGamesBrosYT) - Winner: Video 3-0\n"
        + "VOD: https://www.twitch.tv/videos/569198637"
    )
    result = processRequest(TEST_STRING)
    print(result)
