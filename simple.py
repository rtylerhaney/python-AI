from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Automatically download and set up ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL of the page to scrape
url = 'https://www.football-lineups.com/tourn/Bundesliga_2021-2022/Stats/Tactics/'

def inspect_page_source(url):
    # Load the page
    driver.get(url)
    
    # Give the page time to load the JavaScript content
    time.sleep(5)
    
    # Print the page source to inspect its structure
    page_source = driver.page_source
    print(page_source[:1000])  # Print the first 1000 characters for inspection
    
    # Optionally, save the page source to a file for further inspection
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(page_source)
    
    print("Page source saved to 'page_source.html'")

if __name__ == '__main__':
    inspect_page_source(url)
    
    # Close the Selenium browser
    driver.quit()
