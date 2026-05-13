# Search — listing search

Two endpoints serve listing search, depending on how you want to pass filters.

- `GET /v1/listings` — flat query-string filters, simplest call, sync only.
- `POST /v1/search` — structured JSON body, supports more advanced filters, sync if `maxItems ≤ 50` and async otherwise.

Both return the same row shape. Use the GET form for quick lookups and curl debugging; use the POST form when you need bbox-as-object, boolean amenity filters, or `searchUrls` with a pre-built `searchQueryState`.

## Quick example — GET

```bash
curl -s "https://api.zillapi.com/v1/listings" \
  -G \
  --data-urlencode "status=for_sale" \
  --data-urlencode "bbox=-122.45,37.74,-122.40,37.79" \
  --data-urlencode "price_min=800000" \
  --data-urlencode "price_max=2000000" \
  --data-urlencode "beds_min=2" \
  --data-urlencode "home_types=house,condo,townhouse" \
  --data-urlencode "max_items=20" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  | jq '.data[] | {zpid, address, unformattedPrice, beds, baths, area}'
```

## Quick example — POST

```bash
curl -s "https://api.zillapi.com/v1/search" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "status": "for_sale",
      "bbox": { "west": -122.45, "south": 37.74, "east": -122.40, "north": 37.79 },
      "price": { "min": 800000, "max": 2000000 },
      "beds": { "min": 2 },
      "homeTypes": ["house", "condo", "townhouse"],
      "hasGarage": true
    },
    "maxItems": 50
  }'
```

## Parameters (GET / `filters` body)

| Filter | GET form | POST form (`filters.*`) | Notes |
|---|---|---|---|
| Status | `status=for_sale` | `status: "for_sale"` | `for_sale`, `for_rent`, `sold` |
| Bounding box | `bbox=west,south,east,north` | `bbox: { west, south, east, north }` | **Required.** A free-text `location` alone is rejected with `400 invalid_filters`. |
| Location hint | `location=` | `location:` | Optional decorative hint that flows into the `usersSearchTerm` field; does not replace bbox. |
| Price range | `price_min` / `price_max` | `price: { min, max }` | |
| Beds / baths | `beds_min`, `beds_max`, `baths_min`, `baths_max` | `beds: { min, max }`, `baths: { min, max }` | |
| Sqft | `sqft_min`, `sqft_max` | `sqft: { min, max }` | |
| Year built | `year_built_min`, `year_built_max` | `yearBuilt: { min, max }` | |
| Home types | `home_types=house,condo` | `homeTypes: [...]` | `house`, `condo`, `townhouse`, `multi_family`, `manufactured`, `lot`, `apartment` |
| Days on Zillow | `days_on_zillow=30` | `daysOnZillow: "30"` | `1`, `7`, `14`, `30`, `90`, `6m`, `12m`, `24m`, `36m` |
| Amenities | n/a | `hasPool`, `hasGarage`, `hasAirConditioning`, `hasBasement`, `isWaterfront` | POST only |
| Max items | `max_items` (≤50) | `maxItems` | POST goes async above 50. |
| Output format | `format=json|csv|ndjson` | n/a | GET only. |

## Response shape

```json
{
  "data": [
    {
      "zpid": "...",
      "address": "1 Main St",
      "addressCity": "San Francisco",
      "price": "$1,250,000",
      "unformattedPrice": 1250000,
      "beds": 2,
      "baths": 2,
      "area": 1100,
      "latLong": { "latitude": 37.78, "longitude": -122.41 },
      "statusType": "FOR_SALE",
      "hdpData": { "homeInfo": { "homeStatus": "FOR_SALE", "daysOnZillow": 8 } }
    }
  ],
  "meta": { "count": 50 },
  "request_id": "..."
}
```

**Search rows have a different shape than property-detail records.** Use `beds` / `baths` (not `bedrooms` / `bathrooms`), `address` as a string (not object), `unformattedPrice` for the integer, `latLong` for coords. To enrich a row with the full 300-field record, hit `GET /v1/properties/{zpid}` per zpid — or use `POST /v1/search/with-details` to run search and detail in one chained async job.

## Errors

`400 invalid_filters` (missing or malformed bbox) · `400 invalid_search_url` (POST with a `searchUrls[]` that lacks `?searchQueryState=`) · `401 invalid_api_key` · `402 out_of_credits` · `429 rate_limited`.

## Credit cost

**1 credit per result returned.** A search returning 50 rows costs 50 credits. Failed searches and 0-result searches cost 0 credits. Async batches via `POST /v1/search/with-details` bill the search stage and the detail stage separately.

## See also

- [Full reference — Search](https://zillapi.com/api/search/)
- [extractionMethod modes — pagination, map markers, recursive zoom](https://zillapi.com/blog/zillow-api-search-extraction-methods/)
- [`examples/curl/search_listings.sh`](../examples/curl/search_listings.sh)
- [`examples/python/03_search_listings.py`](../examples/python/03_search_listings.py)
- [`recipes/listing-alerts-cron.md`](../recipes/listing-alerts-cron.md) — polling pattern for new-listing alerts.
