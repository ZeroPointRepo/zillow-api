# Zillow API examples — curl

Three shell scripts. No build step. Requires `curl` and `jq` (both standard on macOS and most Linux distros).

## Setup

```bash
export ZILLAPI_KEY="zk_..."   # get one at https://zillapi.com/signup
```

## Scripts

| File | What it does | Endpoint | Cost |
|---|---|---|---|
| `quickstart.sh` | Look up a property by address, print zpid + Zestimate + beds/baths | `GET /v1/properties/by-address` | 3 credits |
| `lookup_by_address.sh` | Same endpoint with a custom address and verbose field projection | `GET /v1/properties/by-address` | 3 credits |
| `search_listings.sh` | Bounding-box search for active for-sale listings | `GET /v1/listings` | 1 credit per result |

## Run

```bash
bash quickstart.sh
bash lookup_by_address.sh "350 5th Ave, New York, NY 10118"
bash search_listings.sh
```

Failed calls (4xx, 5xx) do not consume credits.
