import csv, json, time, urllib.request
from collections import defaultdict
ETH = ["https://ethereum-rpc.publicnode.com", "https://eth.llamarpc.com"]
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
T = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
D = "0xdf06052f307c8e0ec3bd8cba8e448918905721ec"
H = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
def eth(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for i in range(6):
        try:
            req = urllib.request.Request(ETH[i % len(ETH)], body, H)
            r = json.load(urllib.request.urlopen(req, timeout=30))
            if "error" in r:
                raise Exception(str(r["error"]))
            return r["result"]
        except Exception as e:
            last = e
            time.sleep(1 + i)
    raise last
regts = {}
for r in csv.DictReader(open("rewardclaimer_logs.csv")):
    if r["event"] == "DepositRegistered":
        regts[r["tx"]] = int(json.loads(r["params"])["depositTimestamp"])
rows = list(csv.DictReader(open("ethcheck2.csv")))

out = open("ethcheck5.csv", "w", newline="")
w = csv.writer(out)
w.writerow(["user", "registered_usdc", "ethtx", "eth_block", "eth_time", "registered_time", "tx_from_ok", "tx_to_ok", "input_amount", "note"])
btime = {}
c = defaultdict(int)
for r in rows:
    h = r["ethtx"]
    amt = int(r["registered_usdc"])
    user = r["user"].lower()
    tx = eth("eth_getTransactionByHash", [h])
    if not tx or not tx.get("blockNumber"):
        w.writerow([user, amt, h, "", "", "", "", "", "", "tx_not_found"])
        c["tx_not_found"] += 1
        continue
    blk = int(tx["blockNumber"], 16)
    if blk not in btime:
        btime[blk] = int(eth("eth_getBlockByNumber", [hex(blk), False])["timestamp"], 16)
    inp = tx["input"]
    sel = inp[:10]
    ia = int(inp[10:74], 16) if len(inp) >= 74 else -1
    fok = tx["from"].lower() == user
    tok = (tx["to"] or "").lower() == D
    note = "ok" if (fok and tok and sel == "0xb6b55f25" and ia == amt) else "check"
    c[note] += 1
    w.writerow([user, amt, h, blk, btime[blk], regts.get(r["rayls_tx"], ""), fok, tok, ia, note])
    time.sleep(0.1)
out.close()
print(dict(c))
