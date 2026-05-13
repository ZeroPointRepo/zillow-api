# Zillow API examples — Node.js

Three ES-module scripts using native `fetch`. Zero dependencies, no build step. Works the same in Bun and Deno (substitute the runtime).

## Setup

Node 18 or later required.

```bash
export ZILLAPI_KEY="zk_..."   # get one at https://zillapi.com/signup
```

## Scripts

| File | What it does | Endpoint | Cost |
|---|---|---|---|
| `01_quickstart.mjs` | Look up a property by address, print Zestimate + beds/baths | `/v1/properties/by-address` | 3 credits |
| `02_lookup_by_address.mjs` | Same with `fields` projection | `/v1/properties/by-address` | 3 credits |
| `03_search_listings.mjs` | Bounding-box for-sale listing search | `/v1/listings` | 1 credit per result |

## Run

```bash
node 01_quickstart.mjs
node 02_lookup_by_address.mjs "350 5th Ave, New York, NY 10118"
node 03_search_listings.mjs
```

Or via npm scripts:

```bash
npm run quickstart
npm run lookup
npm run search
```

The scripts throw on non-2xx responses. The error message includes the response status and the API error body so you can see what went wrong.
