import requests
import re
from bs4 import BeautifulSoup

def retrieve_google_doc_content(url):
    """
    This function retrieves the content of the Google Doc using the URL.
    The URL must be a public Google Doc with read access enabled.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_google_doc_data(content):
    """
    This function parses the Unicode characters and coordinates from the Google Doc content.
    """
    soup = BeautifulSoup(content, 'html.parser')

    # Find all rows in the table
    rows = soup.find_all('tr')
    parsed_data = []

    # Skip the header row
    for row in rows[1:]:
        cells = row.find_all('td')
        if len(cells) == 3:
            try:
                x = int(cells[0].get_text(strip=True))
                char = cells[1].get_text(strip=True)
                y = int(cells[2].get_text(strip=True))
                parsed_data.append((char, x, y))
            except ValueError:
                # Skip rows with invalid data
                continue

    return parsed_data

def print_grid(parsed_data):
    """
    This function takes the parsed data (characters and coordinates) and prints the 2D grid.
    """
    # Determine the size of the grid
    if not parsed_data:
        print("No valid character data found in the document.")
        return

    max_x = max(coord[1] for coord in parsed_data)
    max_y = max(coord[2] for coord in parsed_data)

    # Create an empty grid filled with spaces
    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    # Fill the grid with the specified characters
    for char, x, y in parsed_data:
        grid[y][x] = char

    # Print the grid
    for row in grid:
        print(''.join(row))

def extract_and_print_grid(url):
    """
    This function retrieves and parses the data from a Google Doc and prints the resulting character grid.
    """
    content = retrieve_google_doc_content(url)
    parsed_data = parse_google_doc_data(content)
    print_grid(parsed_data)

# Example Usage
url = "https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub"
extract_and_print_grid(url)