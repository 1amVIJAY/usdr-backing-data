import csv, json, os, urllib.request
from collections import defaultdict
from datetime import datetime, timezone
KEY = os.environ["ETHERSCAN_KEY"]
D = "0xdf06052f307c8e0ec3bd8cba8e448918905721ec"
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
OP = "0x0e301beef8daad28f8e38d9fce09112b78fe3161"
u = "https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx"
u += "&contractaddress=" + USDC + "&address=" + D + "&page=1&offset=1000&sort=asc&apikey=" + KEY
rows = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))["result"]
json.dump(rows, open("d_usdc.json", "w"))
deps = set(r["from"].lower() for r in rows if r["to"].lower() == D)
outs = [r for r in rows if r["from"].lower() == D]
def ts(r):
    return datetime.fromtimestamp(int(r["timeStamp"]), timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
reg = {}
for r in csv.DictReader(open("ethcheck5.csv")):
    reg[r["user"].lower()] = int(r["registered_usdc"])
inn = {}
for r in rows:
    if r["to"].lower() == D:
        inn[r["from"].lower()] = int(r["value"])
match = sum(1 for k, v in reg.items() if inn.get(k) == v)
print("registered users", len(reg), "with an equal USDC transfer into D", match)
print("outflows", len(outs), "distinct recipients", len(set(r["to"].lower() for r in outs)))
to_dep = [r for r in outs if r["to"].lower() in deps]
to_op = [r for r in outs if r["to"].lower() == OP]
other = [r for r in outs if r["to"].lower() not in deps and r["to"].lower() != OP]
print("to depositor addresses", len(to_dep), sum(int(r["value"]) for r in to_dep) / 1e6)
print("to 0x0e30", len(to_op), sum(int(r["value"]) for r in to_op) / 1e6)
print("to others", len(other), sum(int(r["value"]) for r in other) / 1e6)
for r in sorted(outs, key=lambda r: -int(r["value"]))[:8]:
    print("LARGEST", ts(r), r["to"], int(r["value"]) / 1e6, r["hash"])
for r in to_op:
    print("TO 0x0e30", ts(r), int(r["value"]) / 1e6, r["hash"])
