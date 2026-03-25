"""
fetch_tickers.py  –  Downloads ~10,000 US stock tickers and saves them to
config/tickers.json  ready for the frontend autocomplete endpoint.

Sources used (all free / no API key required):
  1. NASDAQ-listed stocks  – via NASDAQ FTP (nasdaqlisted.txt)
  2. Other-listed stocks   – via NASDAQ FTP (otherlisted.txt)
  3. yfinance fallback curated list (always included)

Run once:  python fetch_tickers.py
"""

import requests
import json
import os
import io

_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH  = os.path.join(_SCRIPT_DIR, "config", "tickers.json")

# ── Curated fallback (always included even if download fails) ──────────────────
from build_static_tickers import TICKERS as CURATED


def fetch_nasdaq_ftp_tickers():
    """Fetch NASDAQ & NYSE listed tickers from NASDAQ's public FTP data."""
    all_stocks = []
    sources = [
        ("NASDAQ", "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",  0, 1),
        ("NYSE",   "https://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt",   0, 1),
    ]

    for exchange, url, ticker_col, name_col in sources:
        try:
            print(f"  → Fetching {exchange} from {url}")
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            lines = resp.text.strip().split("\n")
            print(f"     Raw lines: {len(lines)}")
            # Skip header (line 0) and footer (last line = file creation info)
            for line in lines[1:-1]:
                parts = line.split("|")
                if len(parts) <= max(ticker_col, name_col):
                    continue
                ticker = parts[ticker_col].strip()
                name   = parts[name_col].strip()
                if not ticker or not name:
                    continue
                # Only skip clearly invalid symbols (spaces, slashes)
                if " " in ticker or "/" in ticker:
                    continue
                all_stocks.append({"ticker": ticker, "name": name, "exchange": exchange})
        except Exception as e:
            print(f"  ⚠ Could not fetch {exchange}: {e}")

    print(f"  → Total fetched (raw): {len(all_stocks)}")
    return all_stocks


def fetch_indian_nse_tickers():
    """Fetch all official listed Indian equities directly from NSE India."""
    import pandas as pd
    import io
    url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36'
    }
    all_stocks = []
    try:
        print(f"  → Fetching INDIAN EQUITIES from {url}")
        r = requests.get(url, headers=headers, timeout=15)
        df = pd.read_csv(io.StringIO(r.text))
        for _, row in df.iterrows():
            sym = str(row.get('SYMBOL', '')).strip()
            name = str(row.get('NAME OF COMPANY', '')).strip()
            if sym and name:
                # Append the explicit suffix mandatory for yfinance
                all_stocks.append({
                    "ticker": f"{sym}.NS",
                    "name": name,
                    "exchange": "NSE"
                })
    except Exception as e:
        print(f"  ⚠ Could not fetch INDIAN EQUITIES: {e}")
    print(f"  → Total fetched (Indian NSE): {len(all_stocks)}")
    return all_stocks

def build_tickers_json():
    print("\n════════════════════════════════════════════")
    print("  QuantTerminal — Ticker Database Builder")
    print("════════════════════════════════════════════\n")

    # 1. Start with curated list
    # Convert from minified keys if necessary:
    normalized_curated = []
    for s in CURATED:
        t = s.get("t") or s.get("ticker")
        n = s.get("n") or s.get("name")
        sec = s.get("s") or s.get("sector")
        normalized_curated.append({"ticker": t, "name": n, "sector": sec})

    print(f"[1/3] Loaded {len(normalized_curated)} curated premium tickers.")
    curated_set = {s["ticker"] for s in normalized_curated}
    combined = list(normalized_curated)

    # 2. Fetch live from NASDAQ FTP & NSE India
    print("[2/3] Fetching live NASDAQ/NYSE & Indian NSE listings...")
    live = fetch_nasdaq_ftp_tickers()
    live.extend(fetch_indian_nse_tickers())
    print(f"      → Fetched {len(live)} total raw tickers from global exchanges.")

    added = 0
    for stock in live:
        if stock["ticker"] not in curated_set:
            combined.append({
                "ticker": stock["ticker"],
                "name":   stock["name"],
                "sector": stock.get("sector", stock.get("exchange", "General"))
            })
            curated_set.add(stock["ticker"])
            added += 1

    print(f"      → Added {added} additional tickers. Total: {len(combined)}")

    # 3. Save
    print("[3/3] Saving to config/tickers.json ...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(combined, f, separators=(',', ':'), ensure_ascii=False)

    print(f"\n✅ Done! {len(combined)} tickers saved to:\n   {os.path.abspath(OUTPUT_PATH)}\n")
    return combined


if __name__ == "__main__":
    tickers = build_tickers_json()
    print("Sample tickers:")
    for t in tickers[:10]:
        print(f"  {t['ticker']:8s} — {t['name']}")
