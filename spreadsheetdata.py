import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import json
#sheet == worksheet
#spreadsheets are composed of sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('authentication.json', scope)
gc = gspread.authorize(credentials)


def getSheetInfo(league):
    sheetID = None
    with open("sheetinfo.json") as f:    
        data = json.load(f)
        spreadsheetID = data["spreadsheetID"]
        sheetID = data[league]
        gRange = data[league+'Range']
        pRange = data[league+'Players']
            
    return (spreadsheetID, sheetID, gRange, pRange)
    
def loadSpreadsheetData(league, players=False):
    spreadsheetID, sheetID, gRange, pRange = getSheetInfo(league)
    spreadsheet = gc.open_by_key(spreadsheetID)
    sheet = spreadsheet.worksheet(sheetID)
    
    game_data = sheet.range(gRange)
    player_names = sheet.range(pRange)

    return (sheet, game_data, player_names)
    
    
if __name__ == '__main__':
    #simple test
    data = loadSpreadsheetData('cc')
    
     