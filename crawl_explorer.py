import json, time, csv, urllib.request, urllib.parse
BASE = "https://explorer.rayls.com/api/v2"
H = {"User-Agent": "Mozilla/5.0"}
JOBS = [
    ("usdr", "/tokens/0x0000000000000000000000000000000000000400/transfers"),
    ("usdce", "/tokens/0x9001dbe4d68d36ab87923a2a9dfb0c745fd25001/transfers"),
]

def get(path, params):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    last = None
    for i in range(6):
        try:
            req = urllib.request.Request(url, headers=H)
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last

for name, path in JOBS:
    f = open("explorer_" + name + ".csv", "w", newline="")
    w = csv.writer(f)
    w.writerow(["type", "block", "timestamp", "tx", "from", "to", "value_raw", "method"])
    params = None
    n = 0
    pg = 0
    while True:
        d = get(path, params)
        for it in d["items"]:
            fr = (it.get("from") or {}).get("hash", "")
            to = (it.get("to") or {}).get("hash", "")
            val = (it.get("total") or {}).get("value", "")
            w.writerow([it["type"], it["block_number"], it["timestamp"], it["transaction_hash"], fr, to, val, it.get("method", "")])
            n += 1
        f.flush()
        pg += 1
        if pg % 20 == 0:
            print(name, "rows", n, flush=True)
        params = d.get("next_page_params")
        if not params:
            break
        time.sleep(0.2)
    f.close()
    print(name, "FINISHED rows", n, flush=True)
print("DONE")
