import re  # Import the regular expression module
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Setup Chrome options to run in headless mode and disable unnecessary features
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--disable-extensions")  # Disable extensions
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model

# Automatically download and set up ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Set the page load timeout to 60 seconds
driver.set_page_load_timeout(60)

# URL of the page to scrape
url = 'https://www.football-lineups.com/tourn/Bundesliga_2021-2022/Stats/Tactics/'

def scrape_with_selenium(url, league, year):
    try:
        # Load the page with the specified timeout
        driver.get(url)
    
        try:
            # Wait explicitly for tables to be available
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, 'table'))
            )
            time.sleep(2)  # Add a brief pause to ensure content is fully loaded

        except TimeoutException:
            print("Page load exceeded 60 seconds, continuing with the scraping process...")
    
        # Locate all tables on the page
        tables = driver.find_elements(By.TAG_NAME, 'table')
        data = []
        
        # Iterate over each table and identify formation data
        for table in tables:
            print("Found a table:")
            rows = table.find_elements(By.TAG_NAME, 'tr')
            table_data = []
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                row_data = [col.text.strip() for col in cols]
                print(row_data)  # Print the content of each row for debugging
                table_data.append(row_data)
            
            # Identify formation data by checking for valid formation patterns
            if len(table_data) > 1 and any(row for row in table_data if row and re.match(r'^\d-\d-\d-\d$', row[1] if len(row) > 1 else '')):
                data.extend([row for row in table_data if any(col.strip() for col in row)])

        # Clean up and save the data if found
        if data:
            df = pd.DataFrame(data).dropna(how='all', axis=1).dropna(how='all', axis=0)
            if len(df.columns) >= 4:  # Ensure we have at least 4 columns
                df = df.iloc[:, [1, 3]]  # Select only the relevant columns (Formation and Count)
                df.columns = ["Formation", "Count"]  # Set the column names
                df['League'] = league
                df['Year'] = year
                df.to_csv('formations_data.csv', index=False)
                print("Data scraping complete and saved to formations_data.csv")
                print(df)
            else:
                print("The table structure did not match the expected format.")
        else:
            print("No matching formation data found.")
    
    except NoSuchElementException as e:
        print(f"Failed to find the table: {e}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Specify the league and year manually
    league = 'Bundesliga'
    year = '2021-2022'
    
    scrape_with_selenium(url, league, year)
    
    # Close the Selenium browser
    driver.quit()
