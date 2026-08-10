# Side-by-side property comparison

**The shortest path: look up the target property by address, pull `/v1/properties/{zpid}/nearby` for comparable zpids, then fetch the detail record for each comparable. Render a Markdown table.** Total cost: 3 + 1 + (4 × 1) = 8 credits for a target plus four comparables.

This is the classic "is this house priced right?" workflow — useful for real-estate analysts, buy-side modelers, and AI agents helping a user evaluate a listing. The Zillow API gives us a nearby-comparables endpoint that returns the top ~12 properties the upstream considers similar.

## End-to-end script

```python
"""compare_properties.py — target + N comparables, rendered as a table."""
import os
import sys

import httpx

KEY = os.environ["ZILLAPI_KEY"]
TARGET_ADDRESS = "350 5th Ave, New York, NY 10118"
N_COMPS = 4

FIELDS = ",".join([
    "zpid", "address", "price", "zestimate", "rentZestimate",
    "bedrooms", "bathrooms", "livingArea", "yearBuilt", "lotSize",
    "homeType", "homeStatus", "taxAssessedValue",
])

def addr_str(prop):
    a = prop["address"]
    return f"{a['streetAddress']}, {a['city']}, {a['state']}"

def money(n):
    return f"${n:,.0f}" if n is not None else "n/a"

def main():
    with httpx.Client(
        base_url="https://api.zillapi.com",
        headers={"Authorization": f"Bearer {KEY}"},
        timeout=30,
    ) as client:
        # 1) Look up the target (3 credits — geocode).
        resp = client.get(
            "/v1/properties/by-address",
            params={"address": TARGET_ADDRESS, "fields": FIELDS},
        )
        resp.raise_for_status()
        target = resp.json()["data"]
        target_zpid = target["zpid"]

        # 2) Pull the nearby comparables sub-resource (1 credit).
        resp = client.get(f"/v1/properties/{target_zpid}/nearby")
        resp.raise_for_status()
        nearby = resp.json()["data"][:N_COMPS]

        # 3) Fetch the full detail for each comparable (1 credit each).
        comps = []
        for c in nearby:
            cz = c.get("zpid") or c.get("hdpData", {}).get("homeInfo", {}).get("zpid")
            if not cz:
                continue
            d = client.get(f"/v1/properties/{cz}", params={"fields": FIELDS})
            if d.status_code == 200:
                comps.append(d.json()["data"])

    # 4) Render the comparison table.
    print(f"# Comparison — {addr_str(target)}\n")
    cols = ["Address", "Price", "Zestimate", "Beds", "Baths", "Sqft", "$/sqft", "Built"]
    print("| " + " | ".join(cols) + " |")
    print("|" + "|".join(["---"] * len(cols)) + "|")
    for prop in [target] + comps:
        zestimate = prop.get("zestimate")
        price = prop.get("price")
        sqft = prop.get("livingArea")
        psf = (zestimate / sqft) if zestimate and sqft else None
        row = [
            addr_str(prop),
            money(price),
            money(zestimate),
            str(prop.get("bedrooms") or "?"),
            str(prop.get("bathrooms") or "?"),
            f"{int(sqft):,}" if sqft else "?",
            f"${psf:,.0f}" if psf else "?",
            str(prop.get("yearBuilt") or "?"),
        ]
        print("| " + " | ".join(row) + " |")

if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPStatusError as e:
        print(f"HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)
```

## Example output

```
# Comparison: 350 5th Ave, New York, NY

| Address | Price | Zestimate | Beds | Baths | Sqft | $/sqft | Built |
|---|---|---|---|---|---|---|---|
| 350 5th Ave, New York, NY | example values | example values | 0 | 0 | 0 | 0 | 0 |
| 22 Maplewood Dr, Greenville, SC | $310,000 | $318,400 | 3 | 2 | 1,508 | $211 | 1962 |
| 14 Beechwood Ave, Greenville, SC | $279,500 | $284,900 | 3 | 1.5 | 1,289 | $221 | 1958 |
| 31 Park Ave, Greenville, SC | $325,000 | $329,800 | 4 | 2 | 1,612 | $205 | 1970 |
| 9 Oakhurst Rd, Greenville, SC | $268,000 | $278,500 | 3 | 2 | 1,371 | $203 | 1961 |
```

That five-row table is enough to answer "is this priced reasonably for the neighborhood." The $/sqft column is the headline — if your target is materially out of line with the comps, that is the first thing to investigate (recent renovations, larger lot, school zoning).

## Tightening the comp set

The `/v1/properties/{zpid}/nearby` endpoint returns whatever the upstream considers similar. Sometimes that includes properties with very different bed counts or square footage. Two filters that help:

```python
def is_useful_comp(target, comp):
    """Return True if the comp is within ±25% on sqft and same bed count."""
    tsq = target.get("livingArea")
    csq = comp.get("livingArea")
    if not tsq or not csq:
        return False
    if abs(csq - tsq) / tsq > 0.25:
        return False
    return target.get("bedrooms") == comp.get("bedrooms")
```

Apply that filter before printing the table, and you get tighter comparables at the cost of some rows. For a more sophisticated comp set, use `POST /v1/search/with-details` with a small bbox around the target plus matching filters — that costs more credits but gives you direct control over the selection.

## Cost summary

| Step | Endpoint | Credits |
|---|---|---|
| Target lookup by address | `/v1/properties/by-address` | 3 |
| Nearby comparables | `/v1/properties/{zpid}/nearby` | 1 |
| Each comparable's detail | `/v1/properties/{zpid}` | 1 per comp |
| **Total for 4 comps** | | **8 credits** |

If you already know the target zpid (skip the geocode), it drops to 6 credits. Cache hits on the detail endpoint are free, so re-running the same comparison within the cache window costs only 1 credit (the `/nearby` call, which is not cached at the same tier).

## See also

- [`endpoints/properties-by-zpid.md`](../endpoints/properties-by-zpid.md) — cache-aware detail lookups.
- [`endpoints/search.md`](../endpoints/search.md) — when you want comparables defined by your own bbox and filters rather than the upstream's `/nearby` heuristic.
- [`recipes/pandas-zestimate-batch.md`](pandas-zestimate-batch.md) — for the same workflow at hundreds-of-properties scale.
