import gspread
from oauth2client.service_account import ServiceAccountCredentials
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


def refresh_credentials():
    global gc
    gc = gspread.authorize(credentials)


def safe_get_sheet(spreadsheet_id, sheet_id, first=True):
    global gc
    try:
        ss = gc.open_by_key(spreadsheet_id)
        result = ss.worksheet(sheet_id)
        return result
    except gspread.exceptions.APIError:
        if not first:
            raise
        else:
            refresh_credentials()
            return safe_get_sheet(spreadsheet_id, sheet_id, False)


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
    sheet = safe_get_sheet(spreadsheetID, sheetID)

    game_data = SplitDatabaseRows(sheet.range(gRange))
    player_data = SplitDatabaseRows(sheet.range(pRange))
    round_data = SplitDatabaseRows(sheet.range(dRange))

    return (sheet, game_data, player_data, round_data)


# splits from a bunch of cells into lists of rows.
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
