# -*- coding: utf-8 -*-
"""Тест Cat D: resources + prompts"""
import json, urllib.request, base64

URL = "http://localhost/PTM_Clean/hs/mcp/mcp"
AUTH = base64.b64encode(b"Admin:").decode()

def call(method, params=None):
    body = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params:
        body["params"] = params
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(URL, data=data,
        headers={"Content-Type": "application/json; charset=utf-8",
                 "Authorization": f"Basic {AUTH}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

# 1. Resources list
print("=== resources/list ===")
r = call("resources/list")
for res in r.get("result", {}).get("resources", []):
    print(f"  {res['uri']} — {res['name']}")

# 2. Resource: ptm://registers
print("\n=== ptm://registers (first 500 chars) ===")
r = call("resources/read", {"uri": "ptm://registers"})
text = r.get("result", {}).get("contents", [{}])[0].get("text", "")
print(text[:500])
print(f"... (total {len(text)} chars)")

# 3. Resource: ptm://business-logic 
print("\n=== ptm://business-logic (first 500 chars) ===")
r = call("resources/read", {"uri": "ptm://business-logic"})
text = r.get("result", {}).get("contents", [{}])[0].get("text", "")
print(text[:500])
print(f"... (total {len(text)} chars)")

# 4. Prompts list
print("\n=== prompts/list ===")
r = call("prompts/list")
for p in r.get("result", {}).get("prompts", []):
    args_str = ", ".join([a["name"] for a in p.get("arguments", [])])
    print(f"  {p['name']}({args_str})")

# 5. Prompt: generate_report_module
print("\n=== generate_report_module (first 300 chars) ===")
r = call("prompts/get", {"name": "generate_report_module", "arguments": {"reportName": "ОстаткиТоваров"}})
if "error" in r:
    print(f"ERROR: {r['error']}")
else:
    text = r["result"]["messages"][0]["content"]["text"]
    print(text[:300])
    print(f"... (total {len(text)} chars)")

# 6. Prompt: generate_form_handlers
print("\n=== generate_form_handlers (first 300 chars) ===")
r = call("prompts/get", {"name": "generate_form_handlers", "arguments": {"metaType": "Documents", "objectName": "ПриходТовара"}})
if "error" in r:
    print(f"ERROR: {r['error']}")
else:
    text = r["result"]["messages"][0]["content"]["text"]
    print(text[:300])
    print(f"... (total {len(text)} chars)")

# 7. Prompt: diagnose_data_integrity
print("\n=== diagnose_data_integrity (first 300 chars) ===")
r = call("prompts/get", {"name": "diagnose_data_integrity", "arguments": {"registerName": "ОстаткиТоваров", "symptom": "Отрицательные остатки товара"}})
if "error" in r:
    print(f"ERROR: {r['error']}")
else:
    text = r["result"]["messages"][0]["content"]["text"]
    print(text[:300])
    print(f"... (total {len(text)} chars)")

# 8. Tools count
print("\n=== tools/list (count) ===")
r = call("tools/list")
tools = r.get("result", {}).get("tools", [])
print(f"Total tools: {len(tools)}")
