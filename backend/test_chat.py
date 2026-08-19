import urllib.request
import json

url = "http://127.0.0.1:8000/api/v1/ai/chat"
data = json.dumps({"message": "hello", "conversation_id": None}).encode("utf-8")
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test"  # Note: assuming auth is bypassed or handled, wait this might 401
}

req = urllib.request.Request(url, data=data, headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Response:", e.read().decode("utf-8"))
except Exception as e:
    print("Error:", e)
