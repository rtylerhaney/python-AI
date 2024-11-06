import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Chrome options to run in incognito mode and disable unnecessary features
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--incognito")  # Run in incognito mode to avoid caching issues
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--disable-extensions")  # Disable extensions
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model

# Automatically download and set up ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Set the page load timeout to 180 seconds
driver.set_page_load_timeout(180)

# Function to generate URLs for the last 10 seasons
def generate_urls(league, start_season, end_season):
    urls = []
    for season in range(start_season, end_season + 1):
        season_url = f"https://www.football-lineups.com/tourn/{league}_{season}-{season+1}/Stats/Tactics/"
        urls.append((season_url, f"{season}-{season+1}"))
    return urls

# Function to scrape data from a given URL
def scrape_with_selenium(url, league, season, retry_count=3):
    data = []
    try:
        # Hard refresh to ensure the correct page is loaded
        driver.get("about:blank")
        driver.execute_script("window.location.href = arguments[0];", url)
    
        try:
            # Wait explicitly for the page to load by checking a unique element (e.g., the season year in the header)
            WebDriverWait(driver, 180).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{season}')]"))
            )
            time.sleep(2)  # Add a brief pause to ensure content is fully loaded

        except TimeoutException:
            print(f"Page load exceeded 180 seconds for {url}, retrying...")
            return scrape_with_selenium(url, league, season, retry_count - 1)

        # Ensure the correct season's page is loaded by verifying the season year in the content
        page_source = driver.page_source
        if season not in page_source:
            print(f"Incorrect page loaded for {season}, retrying...")
            return scrape_with_selenium(url, league, season, retry_count - 1)
    
        # Locate all tables on the page
        tables = driver.find_elements(By.TAG_NAME, 'table')
        
        # Iterate over each table and process matching patterns
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                row_data = [col.text.strip() for col in cols]
                
                # Filter rows to only include those that match the desired format
                if len(row_data) == 4 and row_data[0] == '' and row_data[2] == '':
                    try:
                        count_value = int(row_data[3])  # Ensure the fourth item is an integer
                        # Append data as a tuple with formation as a string, count as an integer, league and season as strings
                        data.append((row_data[1], count_value, league, season))
                    except ValueError:
                        pass  # Skip rows where the fourth item isn't an integer

    except (NoSuchElementException, WebDriverException) as e:
        if retry_count > 0:
            print(f"Error occurred: {e}. Retrying... ({3 - retry_count + 1}/3)")
            time.sleep(5)  # Wait before retrying
            return scrape_with_selenium(url, league, season, retry_count - 1)
        else:
            print(f"Failed to scrape {url} after 3 retries.")
    
    except Exception as e:
        print(f"An error occurred with {url}: {e}")

    return data

if __name__ == '__main__':
    league = 'Bundesliga'
    start_season = 2015
    end_season = 2024

    all_data = []
    urls = generate_urls(league, start_season, end_season)
    
    for url, season in urls:
        print(f"Scraping data from {url} for season {season}")
        season_data = scrape_with_selenium(url, league, season)
        if season_data:
            all_data.extend(season_data)
    
    # Close the Selenium browser
    driver.quit()
    
    # Save the collected data to a CSV file
    with open('football_tactics.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Formation', 'Count', 'League', 'Season'])
        
        # Write the data rows
        for item in all_data:
            # Ensure 'Formation' is a string, 'Count' is an integer, 'League' and 'Season' are strings
            writer.writerow([str(item[0]), int(item[1]), str(item[2]), str(item[3])])
    
    print("Data successfully saved to football_tactics.csv")
