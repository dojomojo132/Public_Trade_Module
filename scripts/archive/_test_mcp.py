"""Test MCP HTTP service endpoint with Basic Auth."""
import urllib.request
import base64

url = "http://localhost/ptm/hs/mcp"
creds = base64.b64encode(b"Admin:").decode()
headers = {"Authorization": f"Basic {creds}"}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print(f"Status: {r.status}")
        body = r.read(400).decode('utf-8', errors='replace')
        print(f"Body: {body}")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.reason}")
    body = e.read(300).decode('utf-8', errors='replace')
    print(f"Body: {body}")
except Exception as e:
    print(f"Error: {e}")
