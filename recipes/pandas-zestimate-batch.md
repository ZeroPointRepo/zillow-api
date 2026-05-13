# Pulling Zillow Zestimates into pandas — batch DataFrame

**The shortest path: loop through addresses with bounded concurrency, normalize the JSON envelopes with `pd.json_normalize`, then `to_csv` or `to_parquet`.** For batches under 100 addresses a sync loop is fastest to write and easiest to reason about. For larger batches use the async `POST /v1/properties/batch` job and pull results from `GET /v1/jobs/{id}/results` once the job completes.

## The single-shot version (under 100 addresses)

```python
import asyncio
import os

import httpx
import pandas as pd

KEY = os.environ["ZILLAPI_KEY"]
ADDRESSES = [
    "17 Zelma Dr, Greenville, SC 29617",
    "350 5th Ave, New York, NY 10118",
    "1600 Pennsylvania Ave NW, Washington DC 20500",
    "1 Infinite Loop, Cupertino, CA 95014",
    # ... up to ~100 here
]
FIELDS = "zpid,address,price,zestimate,rentZestimate,bedrooms,bathrooms,livingArea,yearBuilt"

async def fetch(client, sem, address):
    async with sem:  # bounded concurrency, polite to the rate limit
        resp = await client.get(
            "/v1/properties/by-address",
            params={"address": address, "fields": FIELDS},
        )
        if resp.status_code != 200:
            return {"address_query": address, "_error": resp.status_code}
        row = resp.json()["data"]
        row["address_query"] = address
        return row

async def main():
    sem = asyncio.Semaphore(5)  # 5 concurrent; safe for the free 20/min limit
    async with httpx.AsyncClient(
        base_url="https://api.zillapi.com",
        headers={"Authorization": f"Bearer {KEY}"},
        timeout=30,
    ) as client:
        rows = await asyncio.gather(*(fetch(client, sem, a) for a in ADDRESSES))

    df = pd.json_normalize(rows)
    df.to_csv("zestimates.csv", index=False)
    print(f"Wrote zestimates.csv — {len(df)} rows")

asyncio.run(main())
```

That hits `/v1/properties/by-address` once per row with `fields=zpid,address,price,zestimate,...`, which keeps the response payload small. The semaphore (`asyncio.Semaphore(5)`) caps in-flight requests at 5 — under the free-tier 20/min limit and well under the monthly-tier 200/min ceiling, so you can run this without throttling.

**Cost:** 3 credits per success (the by-address geocode is a paid step). 100 addresses ≈ 300 credits — within the free tier if you only do it once or twice.

## The DataFrame shape

`pd.json_normalize(rows)` flattens the nested `address` object into separate columns:

| Column | Source |
|---|---|
| `zpid` | top-level |
| `address.streetAddress` | nested |
| `address.city` | nested |
| `address.state` | nested |
| `address.zipcode` | nested |
| `zestimate` | top-level |
| `rentZestimate` | top-level |
| `bedrooms`, `bathrooms`, `livingArea`, `yearBuilt` | top-level |
| `address_query` | the raw input string we added ourselves so failures can be traced back |

To keep only the columns you care about, slice before saving:

```python
cols = ["address_query", "zpid", "zestimate", "rentZestimate",
        "bedrooms", "bathrooms", "livingArea", "yearBuilt"]
df[cols].to_csv("zestimates_slim.csv", index=False)
```

## When to switch to the async batch endpoint

For batches above ~200 addresses the sync-loop pattern becomes slow and burns through your per-minute rate limit. The `POST /v1/properties/batch` endpoint exists for exactly this case — submit up to 500 addresses (or Zillow URLs) in one request, receive a `job_id`, and pull the full result set when the job completes.

```python
import time

import httpx

KEY = os.environ["ZILLAPI_KEY"]
ADDRESSES = [...]  # up to 500

with httpx.Client(
    base_url="https://api.zillapi.com",
    headers={"Authorization": f"Bearer {KEY}"},
    timeout=60,
) as client:
    submit = client.post(
        "/v1/properties/batch",
        json={
            "addresses": ADDRESSES,
            "propertyStatus": "FOR_SALE",
            "maxItems": len(ADDRESSES),
        },
    )
    submit.raise_for_status()
    job_id = submit.json()["data"]["job_id"]

    # Poll until done. Real production code uses a webhook — see endpoints/webhooks.md.
    while True:
        time.sleep(5)
        status = client.get(f"/v1/jobs/{job_id}").json()["data"]
        if status["status"] in ("succeeded", "failed", "timed_out", "aborted"):
            break
        print(f"  {status['status']} ({status.get('result_count') or 0} done)")

    if status["status"] != "succeeded":
        raise RuntimeError(f"Job ended: {status}")

    rows = []
    offset, page = 0, 0
    while True:
        page = client.get(
            f"/v1/jobs/{job_id}/results",
            params={"limit": 500, "offset": offset, "format": "json"},
        ).json()
        rows.extend(page["data"])
        if not page["meta"]["has_more"]:
            break
        offset += len(page["data"])

df = pd.json_normalize(rows)
df.to_parquet("zestimates.parquet")
```

The async path costs the same (1 credit per record returned), bypasses the per-minute rate limit, and is faster end-to-end for large batches because the upstream parallelizes the property lookups server-side. Production callers should register a [webhook](../endpoints/webhooks.md) instead of polling — the `job.succeeded` event fires within seconds of completion.

## Common pitfalls

**Don't retry 401 or 402 in a loop.** Those mean configuration is wrong (bad key, no credits) — retrying just delays the inevitable error. Surface them and stop.

**Watch the `address_query` column.** Geocoding occasionally normalizes to the wrong canonical address (a street with multiple suffixes, an apartment number variant). Keep your input string in the DataFrame so you can audit the matches.

**Use `format=ndjson` for very large jobs.** `GET /v1/jobs/{id}/results?format=ndjson` streams the response one record per line, which is friendlier to `pd.read_json(... lines=True)` for million-row exports than holding everything in memory.

## See also

- [`examples/python/05_pandas_dataframe.py`](../examples/python/05_pandas_dataframe.py) — the trimmed-down version of the sync loop.
- [`endpoints/properties-by-address.md`](../endpoints/properties-by-address.md) — full endpoint reference.
- [`endpoints/webhooks.md`](../endpoints/webhooks.md) — webhook signature verification for the async path.
- [Output formats — CSV, NDJSON](https://zillapi.com/blog/zillow-api-formats/)
