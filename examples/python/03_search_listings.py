"""Bounding-box search for active for-sale listings.

`/v1/listings` (GET) accepts a comma-separated `bbox` string in decimal degrees
("west,south,east,north"). The bbox below covers central San Francisco.

Search results use a different field shape than property detail records:
- `address` is a string (not an object)
- `beds` / `baths` (not `bedrooms` / `bathrooms`)
- `unformattedPrice` is the integer; `price` is the pre-formatted display string
- `area` is the living-area sqft

Run:
    export ZILLAPI_KEY="zk_..."
    python 03_search_listings.py
"""
import os

import httpx

KEY = os.environ["ZILLAPI_KEY"]
BBOX = "-122.45,37.74,-122.40,37.79"

resp = httpx.get(
    "https://api.zillapi.com/v1/listings",
    params={
        "status": "for_sale",
        "bbox": BBOX,
        "price_min": 800_000,
        "price_max": 2_000_000,
        "beds_min": 2,
        "home_types": "house,condo,townhouse",
        "max_items": 20,
    },
    headers={"Authorization": f"Bearer {KEY}"},
    timeout=60,
)
resp.raise_for_status()
listings = resp.json()["data"]

print(f"Found {len(listings)} listings\n")
for row in listings:
    print(
        f"  {row.get('address', '?'):40s}  "
        f"${row.get('unformattedPrice') or 0:>10,}  "
        f"{row.get('beds', '?')}bd/{row.get('baths', '?')}ba  "
        f"{row.get('area') or 0:,} sqft"
    )
