import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# Path to your ChromeDriver
driver_path = '/Users/tylerhaney/code/chromedriver'  # Update this to the path where you saved ChromeDriver

# Setup Chrome options (headless mode disabled)
chrome_options = Options()

# Initialize the WebDriver using the Service object
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL for paginated case studies (sorted ascending)
base_url = 'https://www.mitel.com/learn/case-studies#orderby=ASC&page='

# Variable to keep track of page number
page_number = 1
case_study_urls = set()  # Use a set to avoid duplicates
max_retries = 3  # Maximum number of retries for slow-loading pages

# Create a CSV file to store the data
with open('mitel_case_studies.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(['URL', 'Title', 'Content'])

    def scroll_down_page(driver):
        """Scroll down the page to trigger lazy loading if needed"""
        scroll_pause_time = 2
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def clean_text(text):
        """Clean text by removing unwanted characters but keeping punctuation"""
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
        text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"]+', '', text)  # Keep basic punctuation, remove other characters
        return text.strip()

    # Loop through each page and collect URLs
    while True:
        # Construct the URL for the current page
        page_url = base_url + str(page_number)

        # Open the page
        driver.get(page_url)

        retries = 0
        while retries < max_retries:
            try:
                # Scroll down the page to trigger all content loading
                scroll_down_page(driver)

                # Wait for up to 10 seconds for the case studies to load by targeting a known container (div class="col-md-4")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.col-md-4"))
                )

                # Parse the page content with BeautifulSoup after waiting for it to load
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # Find all divs with class "col-md-4"
                case_study_divs = soup.find_all('div', class_='col-md-4')

                # If fewer than 9 case studies are found, grab what's available and stop after this page
                if len(case_study_divs) < 9:
                    print(f"Fewer than 9 case studies found on the last page {page_number}, grabbing remaining URLs and stopping.")
                    break

                break  # Exit retry loop if 9 case studies are found

            except:
                print(f"Failed to load page {page_number}. Retrying...")
                retries += 1
                time.sleep(5)

        # If retries exceeded, stop and exit the entire process
        if retries == max_retries:
            print(f"Max retries exceeded on page {page_number}. Stopping the process.")
            break

        # Extract URLs from the divs
        found_urls = set()
        for div in case_study_divs:
            link = div.find('a', href=True)
            href = link['href'] if link else ''
            if href.startswith('/learn/case-studies/'):
                # Ensure it's a valid URL and add to the set
                full_url = f"https://www.mitel.com{href}"
                found_urls.add(full_url)

        # Add the URLs to our set
        case_study_urls.update(found_urls)

        print(f"Found {len(found_urls)} case studies on page {page_number}")

        # If fewer than 9 case studies are found, assume it's the last page
        if len(case_study_divs) < 9:
            print(f"Finished grabbing all case studies, stopping at page {page_number}.")
            break

        # Move to the next page
        page_number += 1

    # Now visit each URL to extract the title and rendered text content
    for index, url in enumerate(case_study_urls):
        try:
            # Open the case study page
            driver.get(url)
            time.sleep(5)  # Allow the page to load

            # Get the page source
            page_source = driver.page_source

            # Parse the page content
            soup = BeautifulSoup(page_source, 'html.parser')

            # Find the title (usually inside <h1> tag)
            h1_tag = soup.find('h1')
            title = h1_tag.get_text(strip=True) if h1_tag else 'No title found'

            # Extract text from <h1> to <div id="products">
            content = []
            current_tag = h1_tag

            while current_tag and (not current_tag.name == 'div' or not current_tag.get('id') == 'products'):
                if current_tag.name and current_tag.get_text(strip=True):
                    content.append(clean_text(current_tag.get_text(strip=True)))
                current_tag = current_tag.find_next()

            # Now, extract the text inside <div id="products">
            products_div = soup.find('div', id='products')
            if products_div:
                content.append(clean_text(products_div.get_text(strip=True)))
            else:
                content.append("not found")

            # Combine all content
            content_text = ' '.join(content)

            # Write the URL, title, and concatenated text content to the CSV file
            writer.writerow([url, title, content_text])

            print(f"Processed {index + 1}/{len(case_study_urls)}: {url}")

        except Exception as e:
            print(f"Failed to process {url}: {e}")
            writer.writerow([url, "No title found", "not found"])

# Close the WebDriver
driver.quit()

print("All case studies have been processed and saved to 'mitel_case_studies.csv'.")