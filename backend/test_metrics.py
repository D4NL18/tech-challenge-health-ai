import urllib.request
import json
import jwt

# Generate token
token = jwt.encode({"sub": "admin"}, "super-secret-key", algorithm="HS256")

req = urllib.request.Request("http://127.0.0.1:8000/admin/metrics")
req.add_header("Authorization", f"Bearer {token}")

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(f"Number of models: {len(data['data'])}")
        # Check for NaNs or weird values in the first model
        if len(data['data']) > 0:
            print("Keys in first model's metrics:")
            print(data['data'][0]['metrics'].keys())
except Exception as e:
    print(f"Error: {e}")
