# Properties — Look up by address

`GET /v1/properties/by-address`

Look up a single U.S. property by free-form address. The server geocodes the address upstream, resolves the canonical zpid, and returns the full property record — Zestimate, beds, baths, square footage, year built, tax history, school ratings, listing agent, photos, plus the `resoFacts` MLS attribute blob (290+ fields total).

## Quick example

```bash
curl -s "https://api.zillapi.com/v1/properties/by-address" \
  -G --data-urlencode "address=1600 Pennsylvania Ave NW, Washington DC 20500" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  | jq '.data | {zpid, address, zestimate, bedrooms, bathrooms}'
```

## Parameters

| Name | Required | Type | Notes |
|---|---|---|---|
| `address` | yes | string (min 6 chars) | Free-form U.S. address. Street + city + state + zip is recommended; partial addresses work but degrade match quality. |
| `status` | no | enum | `FOR_SALE` (default), `RECENTLY_SOLD`, `FOR_RENT`. Affects which listing snapshot is returned for the same physical property. |
| `fields` | no | string | Comma-separated dotted-path projection. Server trims the response before sending. |

## Response

Envelope: `{ "data": Property, "request_id": "..." }`.

Top-level Property fields shown below — full schema in the [OpenAPI spec](https://zillapi.com/openapi.json) and the [API reference docs](https://zillapi.com/api/properties/).

| Field | Type | Notes |
|---|---|---|
| `zpid` | string | Zillow property ID |
| `address` | object | `{ streetAddress, city, state, zipcode }` |
| `price` | number | Current list price (or last-sold for off-market) |
| `zestimate` | number | Zillow valuation, or `null` if unavailable |
| `rentZestimate` | number | Estimated rent, or `null` |
| `bedrooms` / `bathrooms` | number | |
| `livingArea` | number | Square feet |
| `yearBuilt` | integer | |
| `homeType` | string | `SINGLE_FAMILY`, `CONDO`, `TOWNHOUSE`, etc. |
| `homeStatus` | string | `FOR_SALE`, `RECENTLY_SOLD`, `OFF_MARKET`, etc. |
| `priceHistory`, `taxHistory`, `schools`, `responsivePhotos`, `resoFacts` | arrays / objects | See full schema |

## Errors

`400 invalid_address` · `401 invalid_api_key` · `402 out_of_credits` · `404 not_found` · `429 rate_limited` · `502 upstream_error` · `504 upstream_timeout`.

Failed responses do not consume credits.

## Credit cost

**3 credits per successful call.** The address geocode is a paid upstream operation in addition to the property lookup, which is why this endpoint is priced higher than the URL- or zpid-based lookups. If you already have a zpid, prefer `GET /v1/properties/{zpid}` — it costs 1 credit.

## See also

- [Full reference — `/properties/by-address`](https://zillapi.com/api/properties/)
- [Quickstart](https://zillapi.com/quickstart/)
- [Pricing](https://zillapi.com/blog/zillow-api-pricing/)
- [`examples/python/01_quickstart.py`](../examples/python/01_quickstart.py)
- [`examples/curl/quickstart.sh`](../examples/curl/quickstart.sh)
