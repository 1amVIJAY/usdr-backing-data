import csv
from collections import defaultdict
MINTER = "0xd19a5e28fed41fa289e92ae61b9bc5bd883db0d2"
SUPPLY = 25353233493933504401529
def load(n):
    return list(csv.DictReader(open("explorer_" + n + ".csv")))
u = load("usdr")
c = load("usdce")
mint = [r for r in u if r["type"] == "token_minting"]
burn = [r for r in u if r["type"] == "token_burning"]
mi = sum(int(r["value_raw"]) for r in mint)
bu = sum(int(r["value_raw"]) for r in burn)
print("exact net wei", mi - bu, "gap to supply wei", SUPPLY - (mi - bu))
um = defaultdict(int)
ub = defaultdict(int)
for r in mint:
    um[r["tx"]] += int(r["value_raw"])
for r in burn:
    ub[r["tx"]] += int(r["value_raw"])
ci = defaultdict(int)
co = defaultdict(int)
for r in c:
    if r["to"].lower() == MINTER:
        ci[r["tx"]] += int(r["value_raw"])
    if r["from"].lower() == MINTER:
        co[r["tx"]] += int(r["value_raw"])

def cmp(name, ur, uc):
    both = [t for t in ur if t in uc]
    bad = [t for t in both if ur[t] != uc[t] * 10**12]
    only_u = [t for t in ur if t not in uc]
    only_c = [t for t in uc if t not in ur]
    print(name, "usdr txs", len(ur), "usdc.e txs", len(uc), "both", len(both), "mismatched amounts", len(bad))
    print("  usdr only", len(only_u), sum(ur[t] for t in only_u) / 1e18)
    print("  usdc.e only", len(only_c), sum(uc[t] for t in only_c) / 1e6)
    for t in bad[:15]:
        print("  mismatch", t, ur[t] / 1e18, uc[t] / 1e6)
cmp("MINT vs deposit", um, ci)
cmp("BURN vs withdrawal", ub, co)

def top(rows, label):
    rs = sorted(rows, key=lambda r: -int(r["value_raw"]))[:8]
    for r in rs:
        who = r["to"] if label == "MINT" else r["from"]
        print(label, r["timestamp"][:19], int(r["value_raw"]) / 1e18, r["tx"], who)
top(mint, "MINT")
top(burn, "BURN")
day = defaultdict(int)
for r in burn:
    if r["timestamp"][:7] == "2026-07":
        day[r["timestamp"][:10]] += int(r["value_raw"])
for d in sorted(day):
    print("July burn day", d, day[d] / 1e18)
first = sorted(u, key=lambda r: int(r["block"]))[:6]
for r in first:
    print("EARLIEST", r["type"], r["block"], r["timestamp"][:19], int(r["value_raw"]) / 1e18, r["from"], r["to"])

print("---- unmatched")
when = {}
for r in mint:
    when[r["tx"]] = r["timestamp"][:19]
for t in um:
    if t not in ci:
        print("USDr mint without deposit", when[t], um[t] / 1e18, t)
sender = {}
stamp = {}
for r in c:
    if r["to"].lower() == MINTER:
        sender[r["tx"]] = r["from"]
        stamp[r["tx"]] = r["timestamp"][:19]
for t in ci:
    if t not in um:
        print("USDC.e deposit without mint", stamp[t], ci[t] / 1e6, sender[t], t)
