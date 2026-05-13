# Properties — Look up by Zillow URL

`GET /v1/properties/by-url`

Look up a property when you already have a Zillow.com link. Accepts any `homedetails`, `b` (multi-unit building), `community`, or `apartments` URL. The endpoint parses the URL, hits the upstream property record, and returns the same wrapped envelope as the by-address endpoint.

## Quick example

```bash
curl -s "https://api.zillapi.com/v1/properties/by-url" \
  -G --data-urlencode "url=https://www.zillow.com/homedetails/17-Zelma-Dr-Greenville-SC-29617/11026031_zpid/" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  | jq '.data | {zpid, zestimate, bedrooms, bathrooms}'
```

## Parameters

| Name | Required | Type | Notes |
|---|---|---|---|
| `url` | yes | string (URI) | Full Zillow URL: `homedetails`, `b`, `community`, or `apartments` slugs. |
| `status` | no | enum | `FOR_SALE` (default), `RECENTLY_SOLD`, `FOR_RENT`. |
| `extract_units` | no | enum | `disabled` (default), `all`, `for_sale`, `recently_sold`, `for_rent`, `off_market`. For building URLs (`/b/`), set to `all` to also pull the unit list. |
| `fields` | no | string | Comma-separated dotted-path projection. |

## Response

Envelope: `{ "data": Property, "request_id": "..." }` for single-property URLs.

When `extract_units != "disabled"` and the URL points at a multi-unit building, `data` is an **array** of unit records rather than a single Property object — useful for pulling every unit in a downtown high-rise in one call.

See the [full Property schema](https://zillapi.com/api/properties/) for field-level detail.

## Errors

`400 invalid_url` (URL not a Zillow link) · `400 invalid_status` · `400 invalid_extract_units` · `401 invalid_api_key` · `402 out_of_credits` · `404 not_found` (property record missing upstream) · `502 upstream_error` · `504 upstream_timeout`.

## Credit cost

**1 credit per successful record returned.** For single-property URLs that is 1 credit. For building URLs with `extract_units=all`, the cost scales with the number of units returned.

Failed responses do not consume credits.

## See also

- [Full reference — `/properties/by-url`](https://zillapi.com/api/properties/)
- [Output formats — CSV, NDJSON](https://zillapi.com/blog/zillow-api-formats/)
- [`examples/curl/quickstart.sh`](../examples/curl/quickstart.sh)
- The dedicated [`/buildings/by-url`](https://zillapi.com/api/buildings/) endpoint is the recommended path for building queries because it has stronger schema guarantees on the unit array.
