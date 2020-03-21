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
        if "spreadsheetID" in data:            
            spreadsheetID = data["spreadsheetID"]    
        else:
            raise Exception("Entry " + "'" + "spreadsheetID" + "'" + "not found in sheetinfo.json")
        if league in data:        
            sheetID = data[league]       
            sRange = data[league+'Range']
        else:
            raise Exception("Entry " + "'" + league + "'" + "not found in sheetinfo.json")
            
    return (spreadsheetID, sheetID, sRange)
    
def loadSpreadsheetData(league):    
    spreadsheetID, sheetID, sRange = getSheetInfo(league)
    spreadsheet = gc.open_by_key(spreadsheetID)
    sheet = spreadsheet.worksheet(sheetID)
    cell_list = sheet.range(sRange)
    return (sheet, cell_list)
    
    
if __name__ == '__main__':
    #simple test
    data = loadSpreadsheetData('cc')
    
     