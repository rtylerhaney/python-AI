import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Function to generate URLs for the last 10 seasons for a given league
def generate_urls(league, start_season, end_season):
    urls = []
    for season in range(start_season, end_season + 1):
        season_url = f"https://www.football-lineups.com/tourn/{league}_{season}-{season+1}/Stats/Tactics/"
        urls.append((season_url, f"{season}-{season+1}"))
    return urls

# Function to scrape data using requests and BeautifulSoup
def scrape_with_requests(url, league, season):
    data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "DNT": "1",  # Do Not Track Request Header
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            print(f"Access denied (403) for {url}.")
            return None

        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate all tables on the page
        tables = soup.find_all('table')
        
        # Iterate over each table and process matching patterns
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                row_data = [col.get_text(strip=True) for col in cols]
                
                # Filter rows to only include those that match the desired format
                if len(row_data) == 4 and row_data[0] == '' and row_data[2] == '':
                    try:
                        count_value = int(row_data[3])  # Ensure the fourth item is an integer
                        # Add an apostrophe before the formation number to ensure it's treated as text
                        formation = f"'{row_data[1]}"
                        # Append data as a tuple with formation as a string, count as an integer, league, and season as strings
                        data.append((formation, count_value, league, season))
                    except ValueError:
                        pass  # Skip rows where the fourth item isn't an integer
    except requests.RequestException as e:
        print(f"Error occurred with requests: {e}")
    
    return data

# Fallback function using Selenium if requests fail
def scrape_with_selenium(url, league, season):
    data = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        time.sleep(2)  # Wait for the page to load

        # Locate all tables on the page
        tables = driver.find_elements_by_tag_name('table')
        
        # Iterate over each table and process matching patterns
        for table in tables:
            rows = table.find_elements_by_tag_name('tr')
            for row in rows:
                cols = row.find_elements_by_tag_name('td')
                row_data = [col.text.strip() for col in cols]
                
                # Filter rows to only include those that match the desired format
                if len(row_data) == 4 and row_data[0] == '' and row_data[2] == '':
                    try:
                        count_value = int(row_data[3])  # Ensure the fourth item is an integer
                        formation = f"'{row_data[1]}"  # Add an apostrophe before the formation number
                        data.append((formation, count_value, league, season))
                    except ValueError:
                        pass  # Skip rows where the fourth item isn't an integer
    finally:
        driver.quit()
    
    return data

if __name__ == '__main__':
    leagues = {
        'Bundesliga': 'Bundesliga',
        'La_Liga': 'La Liga',
        'FA_Premier_League': 'Premier League',  # Updated URL key for Premier League
        'Ligue_1': 'Ligue 1',
        'Serie_A': 'Serie A'
    }
    start_season = 2015
    end_season = 2024

    all_data = {}

    # Iterate through each league and season
    for league_key, league_name in leagues.items():
        print(f"Processing league: {league_name}")
        urls = generate_urls(league_key, start_season, end_season)
        
        for url, season in urls:
            print(f"Scraping data from {url} for season {season} in league {league_name}")
            season_data = scrape_with_requests(url, league_name, season)
            if season_data is None:
                print(f"Requests failed, trying Selenium for {season} in league {league_name}")
                season_data = scrape_with_selenium(url, league_name, season)
            if season_data:
                # Add each entry to the dictionary to ensure uniqueness
                for item in season_data:
                    key = (item[0], item[1], item[2], item[3])
                    all_data[key] = item
    
    # Save the collected data to a CSV file
    with open('football_tactics.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Formation', 'Count', 'League', 'Season'])
        
        # Write the data rows
        for item in all_data.values():
            # Ensure 'Formation' is a string, 'Count' is an integer, 'League' and 'Season' are strings
            writer.writerow([str(item[0]), int(item[1]), str(item[2]), str(item[3])])
    
    print("Data successfully saved to football_tactics.csv")
