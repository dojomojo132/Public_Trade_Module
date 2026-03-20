"""Test MCP main endpoint /mcp/mcp."""
import urllib.request
import base64
import json

base = "http://localhost/ptm/hs/mcp"
creds = base64.b64encode(b"Admin:").decode()
headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

# Test the main MCP endpoint used by VS Code
for path in ["/mcp", "/mcp/mcp"]:
    url = base + path
    data = json.dumps({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {}},
        "id": 1
    }).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(600).decode('utf-8', errors='replace')
            print(f"[POST] {url} → {r.status}")
            print(f"  Body: {body[:400]}")
    except urllib.error.HTTPError as e:
        body = e.read(300).decode('utf-8', errors='replace')
        print(f"[POST] {url} → HTTP {e.code}")
        print(f"  Body: {body}")
    except Exception as e:
        print(f"[POST] {url} → ERROR: {e}")
    print()
