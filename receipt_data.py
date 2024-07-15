from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import pandas as pd
from io import BytesIO
import scrape
import time
from selenium.common.exceptions import NoSuchWindowException

# Set up credentials for Azure Form Recognizer   
api_key = "e7f4f26d06124032b9a78112960bf42f"
endpoint = "https://receiptsfr.cognitiveservices.azure.com/"

# Create a Document Analysis client
client = DocumentAnalysisClient(endpoint, AzureKeyCredential(api_key))

# Load image to analyze into a BytesIO object
with open("costco_receipt1.png", "rb") as f:
    image_data = BytesIO(f.read())

# Perform analysis on the receipt image
poller = client.begin_analyze_document("prebuilt-receipt", image_data)
result = poller.result()

# Extract the items
items = []
for receipt in result.documents:
    for item in receipt.fields.get("Items").value:
        item_data = item.value
        
        # Extract item details, ensuring to handle None values safely
        item_name = item_data.get("Description").value if item_data.get("Description") else "N/A"
        item_number = item_data.get("ProductCode").value if item_data.get("ProductCode") else "N/A"
        item_cost = item_data.get("TotalPrice").value if item_data.get("TotalPrice") else "N/A"
        
        try:
            # Scrape additional details for the item
            additional_details = scrape.scrape_additional_details(item_number)

            # Check if additional details indicate that the item does not exist
            if additional_details['Product Name'] == 'Nonexistent':
                # If the item does not exist, skip it
                continue

            # Append the item details and additional details to the list
            items.append({
                "Item Number": item_number,
                "Item Name": item_name,
                "Item Cost": item_cost,
                "Additional Details": additional_details
            })
        except NoSuchWindowException as e:
            print(f"Error: {e}. Skipping item with number: {item_number}")
            continue

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(items)

# Print the DataFrame to verify the results
print(df)
