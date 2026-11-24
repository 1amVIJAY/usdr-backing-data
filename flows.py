import csv
from collections import defaultdict
ESC = "0xd19a5e28fed41fa289e92ae61b9bc5bd883db0d2"
def load(n):
    return list(csv.DictReader(open("explorer_" + n + ".csv")))
u = load("usdr")
c = load("usdce")
dep = set(r["tx"] for r in c if r["to"].lower() == ESC)
early = defaultdict(int)
for r in u:
    if r["type"] == "token_minting" and r["tx"] not in dep:
        early[r["to"].lower()] += int(r["value_raw"])
burntx = set(r["tx"] for r in u if r["type"] == "token_burning")
sent = defaultdict(int)
for r in u:
    if r["tx"] in burntx and r["type"] == "token_transfer" and r["to"].lower() == ESC:
        sent[r["from"].lower()] += int(r["value_raw"])
paid = defaultdict(int)
for r in c:
    if r["from"].lower() == ESC:
        paid[r["to"].lower()] += int(r["value_raw"])

def top(d, scale, label, n):
    for a, v in sorted(d.items(), key=lambda x: -x[1])[:n]:
        print(label, a, v / scale)
top(early, 1e18, "EARLY MINT RECIPIENT USDr", 12)
top(sent, 1e18, "SENT TO ESCROW BEFORE BURN USDr", 12)
top(paid, 1e6, "ESCROW PAID OUT USDC.e", 12)
for a in early:
    if a in sent or a in paid:
        print("OVERLAP", a, "early mint", early[a] / 1e18, "sent to escrow", sent.get(a, 0) / 1e18, "received USDC.e", paid.get(a, 0) / 1e6)
print("counts: early recipients", len(early), "senders to escrow", len(sent), "USDC.e payees", len(paid))
