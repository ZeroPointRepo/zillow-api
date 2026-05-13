# Zillow API examples — Python

Five scripts covering single-property lookups, the dedicated Zestimate sub-resource, listing search, and a pandas batch export. Examples use `httpx` for connection pooling; the `requests` library works identically — swap `httpx.Client()` for `requests.Session()` and the rest is the same.

## Setup

```bash
pip install -r requirements.txt
export ZILLAPI_KEY="zk_..."   # get one at https://zillapi.com/signup
```

## Scripts

| File | What it does | Endpoint | Cost |
|---|---|---|---|
| `01_quickstart.py` | Look up a property by address, print the canonical fields | `/v1/properties/by-address` | 3 credits |
| `02_lookup_by_address.py` | Same with `fields` projection — 90% smaller response | `/v1/properties/by-address` | 3 credits |
| `03_search_listings.py` | Bounding-box for-sale listing search | `/v1/listings` | 1 credit per result |
| `04_zestimate.py` | Resolve a zpid from an address, then call the dedicated Zestimate sub-resource | `/v1/properties/by-address` + `/v1/properties/{zpid}/zestimate` | 3 + 1 credits |
| `05_pandas_dataframe.py` | Look up a list of addresses, normalize into a `DataFrame`, export to CSV | `/v1/properties/by-address` per address | 3 credits each |

## Run

```bash
python 01_quickstart.py
python 02_lookup_by_address.py
python 03_search_listings.py
python 04_zestimate.py
python 05_pandas_dataframe.py
```

Failed responses raise via `resp.raise_for_status()`. The handlers do not retry on 4xx, since 401/402 are configuration issues, not transient errors.
