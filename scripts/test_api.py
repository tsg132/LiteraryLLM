import requests

API_URL = "http://localhost:8000/retrieve"  # Change to ngrok URL if testing from Colab
params = {"query": "What is war?"}

try:
    response = requests.get(API_URL, params=params)
    response.raise_for_status()  # Raise error for bad responses
    print("API Response:", response.json())  # Print retrieved documents
except requests.exceptions.RequestException as e:
    print("Error:", e)
