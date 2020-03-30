from .spreadsheetdata import loadSpreadsheetData
from .matchinfo import ConvertToMatches, GetValidMatches
from .util import modulePath
from os.path import join


import requests
import json
import time
import io

import discord as discordpy

bracketRoot = "http://35.213.253.125:8080/"


def GenerateChannelMessages(league):
    result = []
    result.extend(Header())
    result.extend(GenerateMatches(league))
    result.extend(GenerateScreenshot(league))

    return result


"""Yield successive n-sized chunks from lst."""


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]

def chunkMatches(matches, rounds):
    chunks =  [[] for _ in range(len(rounds))]

    for match in matches:
        for i, round in enumerate(rounds):
            if match.matchNo <= int(round[1].value):
                chunks[i].append(match)
                break
    return chunks

def tabulate(items):
    return "| " + " | ".join(items) + " |\n"


def Header():
    return ["<:stencil:546785001568600074> The Stencil (3.6):  <http://bit.ly/TheStencil>"]


def GenerateMatches(league):
    sheet, game_data, player_names, rounds = loadSpreadsheetData(league)
    result = []
    result.extend(GenerateAllMatches(sheet, game_data, player_names, rounds))
    result.extend(GenerateUnplayedMatches(sheet, game_data, player_names, rounds))
    return result


def GenerateAllMatches(sheet, game_data, player_names, rounds):
    results = []
    matches = ConvertToMatches(game_data)
    message = "**Match List:**\n"
    message += "```javascript\n"
    title = ["M#", "Player1".ljust(20), "Player2".ljust(20), "Score"]
    message += tabulate(title)
    message += "-" * (len(tabulate(title)) - 1) + "\n"
    message += "```\n"
    results.append(message)

    # one message every 8 games.
    for i, chunk in enumerate(chunkMatches(matches, rounds)):
        message = rounds[i][0].value + ".  Due on or before: " + rounds[i][2].value + "\n"
        message += "```javascript\n"
        
        for match in chunk:
            line = [
                str(match.matchNo).rjust(2),
                str(match.player1).ljust(20),
                str(match.player2).ljust(20),
                match.printableScore().rjust(5),
            ]
            message += tabulate(line)
        message += "```\n"
        results.append(message)
    return results


def GenerateUnplayedMatches(sheet, game_data, player_names, rounds):
    matches = ConvertToMatches(game_data)
    matches = GetValidMatches(matches, player_names)
    if len(matches) == 0:
        return "`All matches completed!`"
    results = []
    message = "**Playable Matches:** \n"
    message += "```\n"
    title = ["M#", "Player1".ljust(20), "Player2".ljust(20), "Due".ljust(5),
             "Match time".ljust(19), "Restreamer".ljust(10)]
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
                str(match.player1).ljust(20),
                str(match.player2).ljust(20),
                str(rounds[i][2].value).ljust(5),
                str(match.matchTime).ljust(19),
                rst.ljust(10)
            ]
            message += tabulate(line)
        message += "```\n"
        results.append(message)

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
