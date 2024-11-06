import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# List of URLs for the top 5 leagues
LEAGUES = {
    'EPL': 'https://fbref.com/en/comps/9/Premier-League-Stats',
    'La Liga': 'https://fbref.com/en/comps/12/La-Liga-Stats',
    'Bundesliga': 'https://fbref.com/en/comps/20/Bundesliga-Stats',
    'Serie A': 'https://fbref.com/en/comps/11/Serie-A-Stats',
    'Ligue 1': 'https://fbref.com/en/comps/13/Ligue-1-Stats'
}

# Function to scrape data for a specific league and season
def scrape_formation(league_name, url):
    formations = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all match links for the season
    match_links = [a['href'] for a in soup.find_all('a', href=True) if 'matchlogs' in a['href']]
    
    for link in match_links:
        match_url = f'https://fbref.com{link}'
        match_resp = requests.get(match_url)
        match_soup = BeautifulSoup(match_resp.content, 'html.parser')
        
        # Extract formation data
        try:
            home_team = match_soup.select_one('.teamname').text.strip()
            away_team = match_soup.select_one('.teamname').text.strip()
            home_formation = match_soup.find('div', class_='lineup').text.strip()
            away_formation = match_soup.find('div', class_='lineup').text.strip()
            
            formations.append({
                'league': league_name,
                'home_team': home_team,
                'away_team': away_team,
                'home_formation': home_formation,
                'away_formation': away_formation
            })
        except Exception as e:
            print(f"Error parsing match data: {e}")
        
        # Respectful scraping: Sleep for a while to avoid overwhelming the server
        time.sleep(2)
    
    return formations

def main():
    all_formations = []

    # Loop through the leagues
    for league_name, league_url in LEAGUES.items():
        print(f'Scraping data for {league_name}...')
        league_formations = scrape_formation(league_name, league_url)
        all_formations.extend(league_formations)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_formations)
    
    # Save to CSV
    df.to_csv('formations.csv', index=False)
    print('Data saved to formations.csv')

if __name__ == '__main__':
    main()
