import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import json
from .util import modulePath
from os.path import join

# sheet == worksheet
# spreadsheets are composed of sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    join(modulePath(), "authentication.json"), scope
)
gc = gspread.authorize(credentials)


def getSheetInfo(league):
    sheetID = None
    with open(join(modulePath(), "sheetinfo.json")) as f:
        data = json.load(f)
        spreadsheetID = data["spreadsheetID"]
        sheetID = data[league]
        gRange = data[league + "Range"]
        pRange = data[league + "Players"]
        dRange = data[league + "Dates"]

    return (spreadsheetID, sheetID, gRange, pRange, dRange)


def loadSpreadsheetData(league):
    spreadsheetID, sheetID, gRange, pRange, dRange = getSheetInfo(league)
    spreadsheet = gc.open_by_key(spreadsheetID)
    sheet = spreadsheet.worksheet(sheetID)

    game_data = SplitDatabaseRows(sheet.range(gRange))
    player_data = SplitDatabaseRows(sheet.range(pRange))
    round_data = SplitDatabaseRows(sheet.range(dRange))
    
    return (sheet, game_data, player_data, round_data)

#splits from a bunch of cells into lists of rows.
def SplitDatabaseRows(fullData):
    if len(fullData) == 0:
        return []
    currentRowIdx = None
    currentRow = []
    result = []
    for item in fullData:
        if item.row != currentRowIdx:
            if currentRowIdx is not None:
                result.append(currentRow)
            currentRow = [item]
            currentRowIdx = item.row
        else:
            currentRow.append(item)
    if len(currentRow) > 0:
        result.append(currentRow)

    return result

if __name__ == "__main__":
    # simple test
    data = loadSpreadsheetData("cc")
