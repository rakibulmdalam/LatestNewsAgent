import json, requests

url = "http://127.0.0.1:8000/chat"
payload = {
    "session_id": "dev-123",
    "message": "latest news on AI",
    "prefs_snapshot": {
        "tone": "casual",
        "format": "bullets",
        "interaction": "concise",
        "language": "en",
        "topics": ["technology"]
    }
}
with requests.post(url, json=payload, stream=True) as r:
    r.raise_for_status()
    for line in r.iter_lines(decode_unicode=True):
        if not line: 
            continue
        if line.startswith("data: "):
            event = line[len("data: "):]
            try:
                print(json.loads(event))
            except json.JSONDecodeError:
                print(event)
