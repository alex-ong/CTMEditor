from .spreadsheetdata import loadLeagueData, loadDiscordData
from .matchinfo import ConvertToMatches, GetValidMatches
from .requestinfo import (
    ME,
    CC,
    FC,
    HC,
    CT1,
    CT2,
    CT3,
    CT4,
    CT5,
)
from .util import modulePath
from .scoreentry import ScoreEntry
from os.path import join


import requests
import json
import io

import discord as discordpy

bracketRoot = "http://45.76.119.153:8080/"
leagues = {
    "me": ME + " Masters Event",
    "cc": CC + " Challengers Circuit",
    "fc": FC + " Futures Circuit",
    "hc": HC + " Hopefuls Circuit",
    "ct1": CT1 + " Community Tournament TIER ONE",
    "ct2": CT2 + " Community Tournament TIER TWO",
    "ct3": CT3 + " Community Tournament TIER THREE",
    "ct4": CT4 + " Community Tournament TIER FOUR",
    "ct5": CT5 + " Community Tournament TIER FIVE",
}


def GenerateChannelMessages(league, username_lookup):
    result = []
    result.extend(Header())
    data = loadLeagueData(league)
    ss_discord_ids = loadDiscordData()
    result.extend(GenerateScores(league, data, username_lookup, ss_discord_ids))
    result.extend(GenerateMatches(league, data))
    result.extend(GenerateScreenshot(league))

    return result


"""Yield successive n-sized chunks from lst."""


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def chunkMatches(matches, rounds):
    chunks = [[] for _ in range(len(rounds))]

    for match in matches:
        for i, round in enumerate(rounds):
            if match.matchNo <= int(round[1].value):
                chunks[i].append(match)
                break
    return chunks


def tabulate(items):
    return "| " + " | ".join(items) + " |\n"


def Header():
    return [
        "<:stencil:546785001568600074> The Stencil (3.6):  <http://bit.ly/TheStencil>"
    ]


def MessageHeader(league):
    return "Classic Tetris Monthly - " + leagues[league]


def AssignDiscord(players, db_lookup, ss_lookup):
    not_linked = 0

    for player in players:
        # try database first
        if db_lookup is not None:
            twitch_lower = player.twitch.lower()
            if twitch_lower in db_lookup:
                player.discord = db_lookup[twitch_lower]
        # next, try spreadsheet lookup
        if player.discord is None:
            if ss_lookup is not None:
                if twitch_lower in ss_lookup:
                    player.discord = "[" + ss_lookup[twitch_lower] + "]*"
                    not_linked += 1
        if player.discord is None:
            player.discord = "Use !link"
    return (players, not_linked)


def GenerateScores(league, data, db_lookup, ss_lookup):
    _, _, player_data, _ = data
    players = []
    for player in player_data:
        players.append(ScoreEntry(player))

    players, not_linked_cnt = AssignDiscord(players, db_lookup, ss_lookup)
    result = []

    # get minimum column widths:
    twitch_len = max([len(player.twitch) for player in players])
    discord_len = max([len(str(player.discord)) for player in players])
    country_len = max([len(player.country) for player in players])

    twitch_len = max(twitch_len, len("Twitch"))
    discord_len = max(discord_len, len("Discord"))
    country_len = max(country_len, len("Country"))

    message = "**" + MessageHeader(league) + " - Qualifying Scores**"
    result.append(message)

    for i, chunk in enumerate(chunks(players, 16)):
        message = "```ini\n"
        if i == 0:
            title = [
                "Seed",
                "Twitch".ljust(twitch_len),
                "Discord".ljust(discord_len),
                "Country".ljust(country_len),
                "Score".ljust(8),
            ]
            message += tabulate(title)
            message += "-" * (len(tabulate(title)) - 1) + "\n"
        for player in chunk:
            if len(player.score) == 0:
                continue
            line = [
                str(player.seed).rjust(4),
                str(player.twitch).ljust(twitch_len),
                str(player.discord).ljust(discord_len),
                str(player.country).ljust(country_len),
                str(player.score).ljust(8),
            ]
            message += tabulate(line)
        message += "```\n"
        result.append(message)

    if not_linked_cnt:
        result.append(
            "```ini\n [playername]* : Player has not used `!link`. Someone had to manually add your discord username.\n```"
        )

    result.append("_ _\n" * 2)
    return result


def GenerateMatches(league, data):
    sheet, game_data, player_data, rounds = data
    player_names = [player[0].value for player in player_data]
    result = []
    result.extend(GenerateAllMatches(game_data, rounds, player_names, league))
    result.extend(GenerateUnplayedMatches(game_data, rounds, player_names, league))
    return result


def GenerateAllMatches(game_data, rounds, player_names, league):
    results = []
    matches = ConvertToMatches(game_data)

    # get minimum column widths:
    minPlayer1 = max([len(match.player1) for match in matches])
    minPlayer2 = max([len(match.player2) for match in matches])
    ultraMin = max(minPlayer1, minPlayer2, len("Player1"))

    # one message every 8 games.
    for i, chunk in enumerate(chunkMatches(matches, rounds)):

        message = "**" + MessageHeader(league) + " - " + rounds[i][0].value + "**\n"
        message += "Due on or before: " + rounds[i][2].value + "\n"
        message += rounds[i][3].value + "\n"
        message += "```javascript\n"
        title = ["M#", "Player1".ljust(ultraMin), "Player2".ljust(ultraMin), "Score"]
        message += tabulate(title)
        message += "-" * (len(tabulate(title)) - 1) + "\n"
        for match in chunk:
            if len(match.player1) == 0 or len(match.player2) == 0:
                continue
            line = [
                str(match.matchNo).rjust(2),
                str(match.player1).ljust(ultraMin),
                str(match.player2).ljust(ultraMin),
                match.printableScore().rjust(5),
            ]
            message += tabulate(line)
        message += "```\n"
        message += "_ _\n" * 2
        results.append(message)
    return results


def GenerateUnplayedMatches(game_data, rounds, player_names, league):
    matches = ConvertToMatches(game_data)
    matches = GetValidMatches(matches, player_names)

    # exclude finals
    finals_matchs = int(rounds[-2][1].value)
    matches = list(filter(lambda match: match.matchNo <= finals_matchs, matches))

    if len(matches) == 0:
        return ["`Ready for finals!`"]

    minPlayer1 = max([len(match.player1) for match in matches])
    minPlayer2 = max([len(match.player2) for match in matches])
    ultraMin = max(minPlayer1, minPlayer2, len("Player1"))

    results = []
    message = "**" + MessageHeader(league) + " -  Playable Matches" + "**"
    message += "```\n"
    title = [
        "M#",
        "Player1".ljust(ultraMin),
        "Player2".ljust(ultraMin),
        "Due".ljust(6),
        "Match time".ljust(19),
        "Restreamer".ljust(10),
    ]
    message += tabulate(title)
    message += "-" * (len(tabulate(title)) - 1) + "\n"
    message += "```\n"
    results.append(message)

    for i, chunk in enumerate(chunkMatches(matches, rounds)):
        if len(chunk) == 0:
            continue
        message = "```javascript\n"
        for match in chunk:
            rst = match.restreamer
            rst = rst if len(rst) <= 10 else rst[:7] + "..."
            line = [
                str(match.matchNo).rjust(2),
                str(match.player1).ljust(ultraMin),
                str(match.player2).ljust(ultraMin),
                str(rounds[i][2].value).ljust(6),
                str(match.matchTime).ljust(19),
                rst.ljust(10),
            ]
            message += tabulate(line)
        message += "```\n"

        results.append(message)

    results.append("_ _\n" * 2)
    return results


def GenerateScreenshot(league):
    with open(join(modulePath(), "bracket.json")) as f:
        data = json.load(f)

    for key in list(data.keys()):
        if key != league:
            del data[key]

    postResult = requests.post(bracketRoot + "api/", json=data)
    postJson = postResult.json()
    result = []
    if "files" in postJson:
        for fileName in postJson["files"]:
            response = requests.get(bracketRoot + fileName)
            print(bracketRoot + fileName)
            if response.status_code == 200:
                image_data = io.BytesIO(response.content)
                picture = discordpy.File(image_data, fileName)
                result.append(picture)
    return result
