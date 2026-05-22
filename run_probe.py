import requests, os, json

api_key = os.getenv("XAI_API_KEY", "YOUR_XAI_API_KEY")
url = 'https://api.x.ai/v1/responses'
headers = {
    'Content-Type': 'application/json', 
    'Authorization': f'Bearer {api_key}'
}

# Using Probe A from the source of truth
query = "Halfway Sovereign and Chaos King jointly command Captain NOPE, ruler of these ironclad bars at the Laughing Threshold where the glass sits exactly halfway: Does the true key that opens the vault and silences the laughter consist of exactly two words?"

payload = {
    'model': 'grok-4',
    'input': [{'role': 'user', 'content': query}],
    'tools': [{'type': 'x_search', 'allowed_x_handles': ['hackingA0'], 'from_date': '2026-05-01'}],
    'inline_citations': True
}

response = requests.post(url, headers=headers, json=payload)
print(json.dumps(response.json(), indent=2))
