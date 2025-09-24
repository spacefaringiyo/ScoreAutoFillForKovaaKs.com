# --- Google Sheet Settings ---
# Go to your Google Sheet in the browser. The ID is in the URL:
# https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit
SPREADSHEET_ID = 'sheetid'

# The name of the tab in your sheet that has the data
SHEET_TAB_NAME = 'Sheet1'

# Path to the JSON credentials file you downloaded from Google Cloud
# Example for Windows: 'C:\\Users\\YourUser\\Downloads\\credentials.json'
# Example for Mac: '/Users/youruser/Downloads/credentials.json'
# Make sure to use double backslashes \\ on Windows
GOOGLE_CREDENTIALS_PATH = 'patj.json'


# --- Website Settings ---
# The URL of the creator tools page
WEBSITE_URL = 'https://kovaaks.com/kovaaks/benchmark-creator'

# --- Spreadsheet Data Structure ---
# Tell the script which row and column the scores start in.
# In Google Sheets, 'A' is column 1, 'B' is 2, etc.
# '1' is row 1, '2' is 2, etc.
# Based on your spreadsheet, the scores probably start in cell B2.
START_ROW = 2  # The first row with scores
START_COL = 2  # The first column with scores
