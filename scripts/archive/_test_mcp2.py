"""Test MCP HTTP service endpoints."""
import urllib.request
import base64

base = "http://localhost/ptm/hs/mcp"
creds = base64.b64encode(b"Admin:").decode()
headers = {"Authorization": f"Basic {creds}"}

for path in ["/health", "/rpc", "/"]:
    url = base + path
    method = "POST" if path == "/rpc" else "GET"
    data = b'{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' if path == "/rpc" else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(500).decode('utf-8', errors='replace')
            print(f"[{method}] {url} → {r.status}")
            print(f"  Body: {body[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read(200).decode('utf-8', errors='replace')
        print(f"[{method}] {url} → HTTP {e.code}")
        print(f"  Body: {body}")
    except Exception as e:
        print(f"[{method}] {url} → ERROR: {e}")
    print()
