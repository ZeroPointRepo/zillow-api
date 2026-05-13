# New-listing alerts via cron

**The shortest path: poll `/v1/listings` on a 30-minute cron, diff against a tiny on-disk `seen.json` of zpids, and push the new rows to Slack or Discord.** Webhooks are cleaner if you can host an HTTPS receiver — see the bottom of this recipe for the swap.

The use case is the classic real-estate-investor workflow: track a neighborhood, get notified within minutes when a new listing posts. The Zillow API surface is `/v1/listings` (GET, sync, bbox-filtered) plus a few lines of bookkeeping.

## The polling script

```python
"""new_listing_alerts.py — poll once, alert on deltas."""
import json
import os
import sys
from pathlib import Path

import httpx
import requests as r  # only for the Slack webhook — use urllib if you want zero deps

KEY = os.environ["ZILLAPI_KEY"]
SLACK_WEBHOOK = os.environ["SLACK_WEBHOOK"]  # https://hooks.slack.com/services/...
STATE_FILE = Path(".seen.json")

# Neighborhood: roughly the inner sunset, San Francisco.
BBOX = "-122.475,37.755,-122.450,37.770"
FILTERS = {
    "status": "for_sale",
    "bbox": BBOX,
    "price_min": 1_000_000,
    "price_max": 2_500_000,
    "beds_min": 2,
    "home_types": "house,condo,townhouse",
    "max_items": 50,
}

def fetch_current():
    resp = httpx.get(
        "https://api.zillapi.com/v1/listings",
        params=FILTERS,
        headers={"Authorization": f"Bearer {KEY}"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["data"]

def load_seen():
    if not STATE_FILE.exists():
        return set()
    return set(json.loads(STATE_FILE.read_text()))

def save_seen(zpids):
    STATE_FILE.write_text(json.dumps(sorted(zpids)))

def notify(listing):
    msg = (
        f":house: *New listing* — ${listing.get('unformattedPrice') or 0:,}\n"
        f"{listing.get('address', '?')}, {listing.get('addressCity', '?')}\n"
        f"{listing.get('beds', '?')}bd / {listing.get('baths', '?')}ba · "
        f"{listing.get('area') or '?'} sqft · "
        f"<https://www.zillow.com/homedetails/{listing['zpid']}_zpid/|View on Zillow>"
    )
    r.post(SLACK_WEBHOOK, json={"text": msg}, timeout=10)

def main():
    listings = fetch_current()
    current_zpids = {str(l["zpid"]) for l in listings if l.get("zpid")}
    seen = load_seen()

    new_zpids = current_zpids - seen
    if not new_zpids:
        print("No new listings.")
        return

    for listing in listings:
        if str(listing["zpid"]) in new_zpids:
            notify(listing)

    save_seen(current_zpids | seen)
    print(f"Notified on {len(new_zpids)} new listings.")

if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPStatusError as e:
        # 402 (out of credits) and 401 (bad key) are config errors — surface them.
        print(f"HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)
```

## Crontab line

Run every 30 minutes from 7 AM to 11 PM. (Adjust to your timezone.) The script costs at most ~50 credits per run (50 listings × 1 credit) — well under the monthly tier even at 32 runs/day.

```cron
*/30 7-23 * * *  cd /opt/zillow-alerts && /usr/bin/env ZILLAPI_KEY=zk_... SLACK_WEBHOOK=https://... python3 new_listing_alerts.py >> alerts.log 2>&1
```

For more sensitive watchlists, drop to `*/10` (every 10 minutes) — still safe at the free-tier rate limit.

## Operational notes

**State file should be backed up if it matters.** The `.seen.json` file is the only thing standing between "Slack channel full of duplicate listings" and a clean alert stream. Stick it in `/var/lib/zillow-alerts/seen.json` and back it up nightly if your team relies on the alerts.

**The bbox is the key tuning knob.** Too wide and you'll get noise from neighboring price tiers; too narrow and you'll miss listings just outside the boundary. Two patterns work well:

1. Define the bbox in a `bbox.geojson` file using a tool like [bbox-finder.com](https://bboxfinder.com/), version-control it.
2. For multi-neighborhood watchlists, run the script once per bbox, with a separate `.seen.{name}.json` file per neighborhood.

**Don't try to filter by school, walkability, or other derived attributes in the search endpoint.** `/v1/listings` doesn't expose those filters; what you can do is fetch the full property record for each new zpid (`GET /v1/properties/{zpid}`) and filter client-side. That costs 1 extra credit per new listing.

## The webhook variant

If you have an HTTPS receiver, you can flip the pattern: instead of polling, use `POST /v1/search/with-details` to spawn an async job, register a webhook for `job.succeeded`, and react when the delivery arrives. That trades a few minutes of latency for ~0 ongoing polling traffic.

```python
client.post(
    "/v1/search/with-details",
    json={
        "filters": {
            "status": "for_sale",
            "bbox": {"west": -122.475, "south": 37.755, "east": -122.450, "north": 37.770},
            "price": {"min": 1_000_000, "max": 2_500_000},
        },
        "maxItems": 200,
        "propertyStatus": "FOR_SALE",
    },
)
# Webhook will POST to your receiver with { job_id, status, ... }
```

The receiver pulls results via `GET /v1/jobs/{id}/results` and runs the same delta-against-seen logic shown above. See [`endpoints/webhooks.md`](../endpoints/webhooks.md) for the signature verification details.

## See also

- [`endpoints/search.md`](../endpoints/search.md) — full search reference (filters, response shape).
- [`endpoints/webhooks.md`](../endpoints/webhooks.md) — async job notifications.
- [Search extraction methods](https://zillapi.com/blog/zillow-api-search-extraction-methods/) — pagination vs map markers vs recursive zoom.
