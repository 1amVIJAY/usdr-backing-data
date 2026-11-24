import json, os, urllib.request
from datetime import datetime, timezone
KEY = os.environ["ETHERSCAN_KEY"]
A = "0x0e301beef8daad28f8e38d9fce09112b78fe3161"
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
u = "https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx"
u += "&contractaddress=" + USDC + "&address=" + A + "&page=1&offset=1000&sort=asc&apikey=" + KEY
d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
rows = d.get("result")
print("status", d.get("status"), d.get("message"), "rows", len(rows) if isinstance(rows, list) else rows)
for r in rows:
    v = int(r["value"]) / 1e6
    if v >= 5:
        t = datetime.fromtimestamp(int(r["timeStamp"]), timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        incoming = r["to"].lower() == A
        print(t, "IN " if incoming else "OUT", v, "from" if incoming else "to", r["from"] if incoming else r["to"], r["hash"])
