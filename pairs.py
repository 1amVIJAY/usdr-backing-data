import csv
from collections import defaultdict
ESC = "0xd19a5e28fed41fa289e92ae61b9bc5bd883db0d2"
def load(n):
    return list(csv.DictReader(open("explorer_" + n + ".csv")))
u = load("usdr")
c = load("usdce")
burntx = set(r["tx"] for r in u if r["type"] == "token_burning")
snd = defaultdict(list)
for r in u:
    if r["tx"] in burntx and r["type"] == "token_transfer" and r["to"].lower() == ESC:
        snd[r["tx"]].append((r["from"].lower(), int(r["value_raw"])))
pay = defaultdict(list)
when = {}
for r in c:
    if r["from"].lower() == ESC:
        pay[r["tx"]].append((r["to"].lower(), int(r["value_raw"])))
        when[r["tx"]] = r["timestamp"][:10]

multi = [t for t in pay if len(snd.get(t, [])) != 1 or len(pay[t]) != 1]
print("burn txs with payout", len(pay), "not exactly one sender and one payee", len(multi))
pairs = defaultdict(int)
same = 0
diff = 0
for t in pay:
    if t in multi:
        continue
    s, v = snd[t][0]
    p, w = pay[t][0]
    pairs[(s, p)] += w
    if s == p:
        same += w
    else:
        diff += w
print("USDC.e paid to the sender itself", same / 1e6, "to a different address", diff / 1e6)
for (s, p), w in sorted(pairs.items(), key=lambda x: -x[1])[:15]:
    print("PAIR sender", s, "payee", p, "USDC.e", w / 1e6, "same" if s == p else "different")
dates = defaultdict(list)
for t in pay:
    for p, w in pay[t]:
        dates[p].append(when[t])
for p in dates:
    print("PAYEE", p, "txs", len(dates[p]), "first", min(dates[p]), "last", max(dates[p]))
for tgt in ["0xae68de60b9daadc6ca60725b3c3928ccbd607594", "0xf5df832527a452b7a6e3b7e3cdd3d67249ec03a7"]:
    src = defaultdict(int)
    for r in u:
        if r["to"].lower() == tgt and r["type"] != "token_burning":
            src[r["from"].lower()] += int(r["value_raw"])
    for a, v in sorted(src.items(), key=lambda x: -x[1])[:8]:
        print("INCOMING USDr to", tgt[:10], "from", a, v / 1e18)
