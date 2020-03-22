import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import json
from .util import modulePath
from os.path import join
#sheet == worksheet
#spreadsheets are composed of sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(join(modulePath(),'authentication.json'), scope)
gc = gspread.authorize(credentials)



def getSheetInfo(league):
    sheetID = None
    with open(join(modulePath(),"sheetinfo.json")) as f:    
        data = json.load(f)
        spreadsheetID = data["spreadsheetID"]
        sheetID = data[league]
        gRange = data[league+'Range']
        pRange = data[league+'Players']
            
    return (spreadsheetID, sheetID, gRange, pRange)
    
def loadSpreadsheetData(league):
    spreadsheetID, sheetID, gRange, pRange = getSheetInfo(league)
    spreadsheet = gc.open_by_key(spreadsheetID)
    sheet = spreadsheet.worksheet(sheetID)
    
    game_data = sheet.range(gRange)
    player_names = sheet.range(pRange)
    player_names = [item.value for item in player_names] #convert to string

    return (sheet, game_data, player_names)
    
    
if __name__ == '__main__':
    #simple test
    data = loadSpreadsheetData('cc')
    
     