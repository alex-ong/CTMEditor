import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "authentication.json", scope
)
with open("sheetinfo.json") as f:
    data = json.load(f)
    sheetName = data["sheetID"]
gc = gspread.authorize(credentials)


wks = gc.open_by_key(sheetName)
ccEditor = wks.worksheet("CTMCC Results")

t = time.time()
cell_list = ccEditor.range("B2:G30")

print(time.time() - t)
