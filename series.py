import csv
from datetime import date, timedelta
from collections import defaultdict
MINTER = "0xd19a5e28fed41fa289e92ae61b9bc5bd883db0d2"
EXTRA = 20010 * 10**18
sup = defaultdict(int)
res = defaultdict(int)
for r in csv.DictReader(open("explorer_usdr.csv")):
    v = int(r["value_raw"])
    d = r["timestamp"][:10]
    if r["type"] == "token_minting":
        sup[d] += v
    if r["type"] == "token_burning":
        sup[d] -= v
for r in csv.DictReader(open("explorer_usdce.csv")):
    v = int(r["value_raw"])
    d = r["timestamp"][:10]
    if r["to"].lower() == MINTER:
        res[d] += v * 10**12
    if r["from"].lower() == MINTER:
        res[d] -= v * 10**12
days = sorted(set(sup) | set(res))

print("first mint/burn day", min(sup), "first minter USDC.e day", min(res))
s = 0
b = 0
rows = []
d = date.fromisoformat(days[0])
end = date.fromisoformat(days[-1])
while d <= end:
    k = d.isoformat()
    s += sup.get(k, 0)
    b += res.get(k, 0)
    rows.append((k, s, b))
    d += timedelta(days=1)
short = None
for i, (k, s, b) in enumerate(rows):
    if i % 7 == 0 or i == len(rows) - 1:
        print(k, "supply(events)", round(s / 1e18, 2), "supply(+20010)", round((s + EXTRA) / 1e18, 2), "minter USDC.e", round(b / 1e18, 2))
    if b < s + EXTRA and short is None:
        short = k
    if b >= s + EXTRA and short is not None:
        print("reserve below supply(+20010) from", short, "to", k)
        short = None
if short:
    print("reserve below supply(+20010) from", short, "to end")
