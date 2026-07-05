import requests
import time
import sys

API_URL = "http://localhost:8000/api"

print("Triggering single batch ingestion...")
response = requests.post(f"{API_URL}/ingest")
if response.status_code == 200:
    data = response.json()
    print(f"Processed {data['processed']} invoices:")
    for inv in data['invoices']:
        print(f" - Invoice ID {inv['id']}: {inv['status']}")
else:
    print(f"Error: {response.text}")


