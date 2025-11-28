# test_a2a_client.py
import requests
import json

url = "http://localhost:8100/.well-known/agent-card.json"
response = requests.get(url)
print("Agent Card:", json.dumps(response.json(), indent=2))