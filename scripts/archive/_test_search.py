"""Quick test of /search endpoint."""
import urllib.request, ssl, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["мол", "хле", "xyz999"]
for q in queries:
    url = "https://localhost/ptm/hs/mobile/search?q=" + urllib.parse.quote(q)
    try:
        resp = urllib.request.urlopen(url, timeout=10, context=ctx)
        body = resp.read().decode("utf-8")
        data = json.loads(body)
        count = data.get("count", 0)
        print(f"Query '{q}': {count} results")
        for item in data.get("items", [])[:5]:
            name = item.get("name", "")
            price = item.get("price", 0)
            barcode = item.get("barcode", "")
            print(f"  - {name} | {price} | ШК: {barcode}")
    except urllib.error.HTTPError as e:
        print(f"Query '{q}': HTTP {e.code}")
    except Exception as e:
        print(f"Query '{q}': ERROR {e}")
