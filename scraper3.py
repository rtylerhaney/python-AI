from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
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

# Set the page load timeout to 30 seconds
driver.set_page_load_timeout(30)

# URL of the page to scrape
url = 'https://www.football-lineups.com/tourn/Bundesliga_2021-2022/Stats/Tactics/'

def scrape_with_selenium(url):
    try:
        # Load the page with the specified timeout
        driver.get(url)
    
        try:
            # Wait explicitly for tables to be available
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, 'table'))
            )
            time.sleep(2)  # Add a brief pause to ensure content is fully loaded

        except TimeoutException:
            print("Page load exceeded 30 seconds, continuing with the scraping process...")
    
        # Locate all tables on the page
        tables = driver.find_elements(By.TAG_NAME, 'table')
        data = []
        table_found = False
        
        # Iterate over each table until the first matching pattern is found
        for table in tables:
            if table_found:
                break

            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                row_data = [col.text.strip() for col in cols]
                
                # Filter rows to only include those that match the desired format
                if len(row_data) == 4 and row_data[0] == '' and row_data[2] == '':
                    try:
                        int(row_data[3])  # Ensure the fourth item is an integer
                        data.append(row_data)
                        print(row_data)  # Print the valid data row for debugging
                        table_found = True
                    except ValueError:
                        pass  # Skip rows where the fourth item isn't an integer
        
        # The 'data' list now contains only the rows in the specified format from the first matching table
    
    except NoSuchElementException as e:
        print(f"Failed to find the table: {e}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    scrape_with_selenium(url)
    
    # Close the Selenium browser
    driver.quit()
