# -*- coding: utf-8 -*-
"""Test POST /api/check - create receipt"""
import urllib.request
import json

url = "http://localhost/ptm/hs/api/check"

data = {
    "items": [
        {
            "code": "725",
            "quantity": 2,
            "price": 1132
        },
        {
            "code": "000000126",
            "quantity": 1
        }
    ],
    "payments": [
        {
            "type": "Наличные",
            "amount": 2498
        }
    ]
}

json_data = json.dumps(data, ensure_ascii=False).encode("utf-8")

req = urllib.request.Request(
    url,
    data=json_data,
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST"
)

try:
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"Status: {resp.status}")
    body = resp.read().decode("utf-8")
    print(f"Body: {body}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    body = e.read().decode("utf-8")
    print(f"Body: {body}")
except Exception as e:
    print(f"Error: {e}")
