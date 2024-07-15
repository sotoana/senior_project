from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from io import BytesIO
import re
import time
import pandas as pd

# Set up credentials for Azure Computer Vision
subscription_key = "7c239e064ca445d1971b6adf13eb6fcd"
endpoint = "https://receiptsinfo.cognitiveservices.azure.com/"

# Create a Computer Vision client
credentials = CognitiveServicesCredentials(subscription_key)
client = ComputerVisionClient(endpoint, credentials)

# Load image to analyze into a BytesIO object
with open("costco_receipt1.png", "rb") as f:
    image_data = BytesIO(f.read())

# Perform OCR on the receipt image
result = client.read_in_stream(image_data, raw=True)

# Get the operation ID from the response headers
operation_location = result.headers["Operation-Location"]
operation_id = operation_location.split("/")[-1]

# Get the result of the OCR operation
while True:
    result = client.get_read_result(operation_id)
    if result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
        break
    time.sleep(1)

# Process the OCR results
if result.status == OperationStatusCodes.succeeded:
    ocr_lines = [line.text for line in result.analyze_result.read_results[0].lines if not any(keyword in line.text for keyword in ["APPROVED", "PURCHASE", "DEBIT", "TOTAL", "(A)", "INSTANT SAVINGS", "TAX"]) and "LINE" not in line.text]
else:
    print("OCR operation failed or not completed.")
    ocr_lines = []

# Define a regular expression to match item details
item_pattern = re.compile(r'(\d+)\s+([A-Z\s]+)\s+(\d+\.\d{2})')
secondary_item_pattern = re.compile(r'(\d+\.\d{2})')

# Define a regular expression to match date formats (adjust as per your receipt format)
date_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')

# Extract item details and date
items = []
receipt_date = None

for line in ocr_lines:
    primary_match = item_pattern.match(line)
    if primary_match:
        item_number, item_name, item_cost = primary_match.groups()
        if item_number.isdigit():  # Check if item number is numeric
            discount = 1 if "/" in item_name else 0
            items.append({
                "Item Number": item_number,
                "Item Name": item_name.strip(),
                "Item Cost": item_cost,
                "Discount": discount
            })
    elif secondary_item_pattern.search(line):
        previous_line = ocr_lines[ocr_lines.index(line) - 1]
        if ' ' in previous_line:
            item_number, item_name = previous_line.strip().split(' ', 1)
            item_cost = secondary_item_pattern.search(line).group(0)
            if item_number.isdigit():  # Check if item number is numeric
                discount = 1 if "/" in item_name else 0
                items.append({
                    "Item Number": item_number,
                    "Item Name": item_name.strip(),
                    "Item Cost": item_cost,
                    "Discount": discount
                })
    # Extract date from the line
    date_match = date_pattern.search(line)
    if date_match:
        receipt_date = date_match.group(1)

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(items)

# Add the receipt date to the DataFrame
if receipt_date:
    df['Receipt Date'] = receipt_date

# Print the DataFrame to verify the results
print(df)
