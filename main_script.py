import time

# config.py should be in the same directory and contain these variables.
# If it's not, you can define them directly here.
from config import SPREADSHEET_ID, SHEET_TAB_NAME, GOOGLE_CREDENTIALS_PATH, WEBSITE_URL, START_ROW, START_COL

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException # Import for better error handling

# Google Sheets API imports
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ---
# SETUP INSTRUCTIONS:
# 1. Make sure you have a `config.py` file with all the required variables.
#    Example `config.py`:
#    SPREADSHEET_ID = 'your_google_sheet_id_here'
#    SHEET_TAB_NAME = 'Sheet1'
#    GOOGLE_CREDENTIALS_PATH = 'path/to/your/credentials.json'
#    WEBSITE_URL = 'https://your-target-website.com/login'
#    START_ROW = 2  # The first row with data in your Google Sheet (e.g., row 2)
#    START_COL = 1  # The first column with data in your Google Sheet (e.g., column A)
#
# 2. Ensure your Google service account has "Viewer" access to the Google Sheet.
# ---

def get_sheet_data():
    """Connects to the Google Sheets API and fetches the score data."""
    print("Connecting to Google Sheets...")
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_TAB_NAME).execute()
        all_data = result.get('values', [])
        
        if not all_data or len(all_data) < START_ROW:
            print("No data found in the sheet or START_ROW is out of bounds.")
            return None
        
        # Slicing the data correctly based on start row and column
        score_data = [row[START_COL-1:] for row in all_data[START_ROW-1:]]
        print(f"Successfully fetched {len(score_data)} rows of score data.")
        return score_data
    except Exception as e:
        print(f"An error occurred while fetching data from Google Sheets: {e}")
        return None

def automate_website(score_data):
    """Launches a browser, navigates to the website, and enters the scores."""
    if not score_data:
        print("No score data provided to automate. Exiting.")
        return

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(WEBSITE_URL)

    print("\nACTION REQUIRED: Please log in and navigate to the benchmark editor.")
    input("After you see the data grid, press Enter in this console to continue...")
    
    try:
        # A "landmark" element to confirm the main table page has loaded.
        # This could be the table header.
        landmark_xpath = '/html/body/div[2]/div[3]/div/div[2]/div[3]/table/thead/tr/th[1]/div'
        wait = WebDriverWait(driver, 30)
        wait.until(EC.visibility_of_element_located((By.XPATH, landmark_xpath)))
        print("Creator Tools page is loaded. Preparing for data entry...")

        total_rows_from_sheet = len(score_data)
        
        # --- The Robust Looping Architecture ---
        # Loop through each row by its index rather than a pre-fetched list of elements.
        # This avoids stale element exceptions.
        for row_index in range(total_rows_from_sheet):
            current_row_num = row_index + 1  # XPath is 1-based, our loop is 0-based
            print(f"\nProcessing row {current_row_num}...")
            
            # Use a try-except block for each row to make the script resilient.
            try:
                # 1. Find the specific row for THIS iteration.
                row_xpath = f"//table/tbody/tr[{current_row_num}]"
                row_element = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))

                # 2. Scroll this specific row into the middle of the screen to trigger rendering.
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row_element)
                
                # 3. **CRITICAL FIX**: Wait for the inputs INSIDE this row to be present.
                #    This replaces the unreliable `time.sleep()` and uses the CORRECTED XPath.
                input_xpath_in_row = ".//td/input"
                boxes_in_this_row = WebDriverWait(row_element, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, input_xpath_in_row))
                )

                scores_for_this_row = score_data[row_index]
                
                if len(boxes_in_this_row) != len(scores_for_this_row):
                    print(f"!! MISMATCH on row {current_row_num}: Found {len(boxes_in_this_row)} boxes but have {len(scores_for_this_row)} scores. Skipping row.")
                    continue

                # 4. Fill in the boxes for this now-guaranteed-to-be-ready row.
                for col_index, input_box in enumerate(boxes_in_this_row):
                    score = scores_for_this_row[col_index]
                    try:
                        # Use JavaScript to directly set value and trigger events, which is
                        # often more reliable for modern web frameworks (React, Vue, etc.).
                        driver.execute_script("arguments[0].value = arguments[1];", input_box, str(score))
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_box)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", input_box)
                        print(f"  - Inputted score '{score}' into column {col_index + 1}")
                    except Exception as e:
                        print(f"!! FAILED to input on row {current_row_num}, col {col_index + 1}: {e}")

            except TimeoutException:
                print(f"!! FAILED to find row {current_row_num} or its inputs within the time limit. Skipping.")
                continue
            except Exception as e:
                print(f"!! An unexpected error occurred on row {current_row_num}: {e}. Skipping.")
                continue

        print("\n\nData entry complete!")
        print("You can now Save or Publish. The browser will remain open.")
        input("Press Enter in this console to close the browser...")

    except TimeoutException:
        print("\n--- ERROR: Could not find the initial data grid/table on the page.")
        print("Please make sure you are on the correct page before pressing Enter.")
    except Exception as e:
        print(f"\n--- AN UNEXPECTED ERROR OCCURRED --- {e}")
        
    finally:
        print("Closing browser.")
        driver.quit()

if __name__ == "__main__":
    data = get_sheet_data()
    if data:
        automate_website(data)