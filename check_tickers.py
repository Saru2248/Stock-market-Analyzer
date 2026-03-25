import json
d = json.load(open(r"config\tickers.json", encoding="utf-8"))
print("Total tickers:", len(d))
for x in d[:10]:
    print(f"  {x['ticker']:8s} - {x['name']}")
# Count by sector
from collections import Counter
sectors = Counter(x.get("sector","?") for x in d)
print("\nBy sector:")
for s, c in sectors.most_common():
    print(f"  {c:5d}  {s}")
