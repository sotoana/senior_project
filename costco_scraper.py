from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys

# Function to search for an item on the Costco website
def search_item(driver, item_number):
    search_box = driver.find_element(By.ID, "search-field")
    search_box.send_keys(20 * Keys.BACKSPACE)  # Clear the search box before entering a new item number
    search_box.send_keys(item_number)
    search_box.submit()

# Function to extract item description from the search results page
def extract_item_description(driver):
    try:
        # Use explicit waits to ensure the description element is present
        description_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-info-description"))  # Update this selector based on the actual structure
        )
        description_text = description_element.text.strip()
        return description_text
    except Exception as e:
        print(f"Error extracting description: {str(e)}")
        return "Not Found"

# Path to the Microsoft Edge WebDriver executable
webdriver_path = r"C:\Users\ana8s\OneDrive\Documents\BYU-IDAHO\DS 499\msedgedriver.exe"

# Create Microsoft Edge WebDriver
driver = webdriver.Edge(executable_path=webdriver_path)

# Open Costco website
driver.get("https://www.costco.com")

# Wait for the page to load
time.sleep(5)

# Item numbers to scrape
item_numbers = [
    "1618252",
    "1361170",
    "897971",
    "1721498",
    "1485984"
]

# Dictionary to store item details
item_details = {}

# Search for each item number and extract item description
for item_number in item_numbers:
    try:
        search_item(driver, item_number)
        time.sleep(5)  # Wait for the search results page to load
        item_details[item_number] = extract_item_description(driver)
    except Exception as e:
        print(f"Error searching for item {item_number}: {str(e)}")
        item_details[item_number] = "Not Found"
        continue
    finally:
        search_box = driver.find_element(By.ID, "search-field")
        search_box.clear()  # Clear the search box before the next iteration

# Close the browser
driver.quit()

# Print the scraped item details
for item_number, description in item_details.items():
    print(f"Item Number: {item_number}")
    print(f"Item Description: {description}")
    print("="*30)
