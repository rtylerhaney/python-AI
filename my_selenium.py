from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Initialize Chrome WebDriver with ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Use the driver as needed, for example:
driver.get("https://www.google.com")

# Don't forget to close the driver when done
driver.quit()
