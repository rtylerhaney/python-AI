import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = 'https://www.football-lineups.com/tourn/Bundesliga_2021-2022/Stats/Tactics/'

# Custom headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def scrape_single_row(url):
    # Send a GET request to the website with headers
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Successfully connected to the site!")
    else:
        print(f"Failed to connect to the site. Status code: {response.status_code}")
        return
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for tables and try to find the one with formation data
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        # Check if table has enough rows and columns
        if len(rows) > 1 and len(rows[0].find_all('td')) > 1:
            # Check the content of the first row for formation-like patterns
            first_row = rows[1]
            cols = first_row.find_all('td')
            if len(cols) >= 2:
                first_col_text = cols[0].text.strip()
                second_col_text = cols[1].text.strip()
                
                # We expect the first column to contain a formation pattern and the second to be numerical
                if ('-' in first_col_text or '3' in first_col_text) and second_col_text.isdigit():
                    print(f"Found the formation data:")
                    print(f"Formation: {first_col_text}, Count: {second_col_text}")
                    return

    print("No relevant formation data table found.")

if __name__ == '__main__':
    scrape_single_row(url)
