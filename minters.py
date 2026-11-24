import json, time, urllib.request, urllib.parse
from collections import defaultdict
A = "0x07E17E17E17E17e17E17e17e17e17e17E17E17E6"
H = {"User-Agent": "Mozilla/5.0"}
params = None
cnt = defaultdict(int)
amt = defaultdict(int)
while True:
    u = "https://explorer.rayls.com/api/v2/addresses/" + A + "/logs"
    if params:
        u += "?" + urllib.parse.urlencode(params)
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60))
    for it in d["items"]:
        dec = it.get("decoded") or {}
        name = (dec.get("method_call") or "").split("(")[0]
        if name in ("Minted", "Burned"):
            vals = [p.get("value") for p in dec.get("parameters") or []]
            cnt[(name, vals[0])] += 1
            amt[(name, vals[0])] += int(vals[-1])
    params = d.get("next_page_params")
    if not params:
        break
    time.sleep(0.2)
for k in sorted(cnt):
    print(k, cnt[k], amt[k] / 1e18)
