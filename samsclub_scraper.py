from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# Function to search for an item on the Sam's Club website
def search_item(driver, item_number):
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#input_search"))
        )
        search_box.clear()
        search_box.send_keys(item_number)
        search_box.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"Error searching for item {item_number}: {str(e)}")

# Function to extract item details from the search results page
def extract_item_details(driver):
    item_details = {}
    try:
        item_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sc-item-card"))
        )
        
        for item_element in item_elements:
            try:
                item_number_element = item_element.find_element(By.CSS_SELECTOR, ".sc-item-id")
                description_element = item_element.find_element(By.CSS_SELECTOR, ".sc-item-description")
                item_number = item_number_element.text.strip()
                description = description_element.text.strip()
                item_details[item_number] = description
            except Exception as e:
                print(f"Error extracting details for an item: {str(e)}")
                continue
        
        return item_details
    
    except Exception as e:
        print(f"Error extracting item details: {str(e)}")
        return {}

# Path to the Microsoft Edge WebDriver executable
webdriver_path = r"C:\Users\ana8s\OneDrive\Documents\BYU-IDAHO\DS 499\msedgedriver.exe"

# Create Microsoft Edge WebDriver
driver = webdriver.Edge(executable_path=webdriver_path)

# Open Sam's Club website
driver.get("https://www.samsclub.com/")

# Wait for the page to load
time.sleep(5)

# Item numbers to search
item_numbers = [
    "15016"
]

# Dictionary to store item details
item_details = {}

# Search for each item number and extract item details
for item_number in item_numbers:
    try:
        search_item(driver, item_number)
        time.sleep(5)  # Wait for the search results page to load
        item_details[item_number] = extract_item_details(driver)
    except Exception as e:
        print(f"Error searching for item {item_number}: {str(e)}")
        item_details[item_number] = {}
        continue

# Close the browser
driver.quit()

# Print the scraped item details
for item_number, details in item_details.items():
    print(f"Item Number: {item_number}")
    for item_number, description in details.items():
        print(f"Item Description: {description}")
    print("=" * 30)
