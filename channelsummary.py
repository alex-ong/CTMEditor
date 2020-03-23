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

    result.append(GenerateUnplayedMatches(league))
    screenshots = GenerateScreenshot(league)
    for picture in screenshots:
        result.append(picture)

    return result


def tabulate(items):
    return "| " + " | ".join(items) + " |\n"


def GenerateUnplayedMatches(league):
    sheet, game_data, player_names = loadSpreadsheetData(league)
    matches = ConvertToMatches(game_data)
    matches = GetValidMatches(matches, player_names)
    result = "Playable Matches: \n"
    result += "```\n"
    title = ["M#", "Player1".ljust(15), "Player2".ljust(15)]
    result += tabulate(title)
    result += "-" * (len(tabulate(title)) - 1) + "\n"
    for match in matches:
        line = [
            str(match.matchNo).rjust(2),
            str(match.player1).ljust(15),
            str(match.player2).ljust(15),
        ]
        result += tabulate(line)
    result += "```\n"
    return result


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
