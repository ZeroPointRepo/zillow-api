# Properties — Look up by zpid

`GET /v1/properties/{zpid}`

The cheapest, fastest way to fetch a property record — pass the Zillow `zpid` directly. The response is cache-served when fresh, and the envelope includes a `cached` boolean and `fetched_at` timestamp so you can tell whether the upstream was hit.

Prefer this endpoint when you already have a zpid (from a previous `/by-address` call, a search result, or your own database). It avoids the 3-credit geocode hop and supports cache-friendly polling for properties you're tracking over time.

## Quick example

```bash
curl -s "https://api.zillapi.com/v1/properties/11026031" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  | jq '{cached, fetched_at, zpid: .data.zpid, zestimate: .data.zestimate}'
```

## Parameters

| Name | In | Required | Type | Notes |
|---|---|---|---|---|
| `zpid` | path | yes | string (numeric) | Zillow property ID. Must match `^[0-9]+$`. |
| `fields` | query | no | string | Comma-separated dotted-path projection. |

## Response

Envelope: `{ "data": Property, "cached": boolean, "fetched_at": ISO-8601, "request_id": "..." }`.

- `cached: true` — the response was served from the cache layer. No upstream hit, no credit charged.
- `cached: false` — fresh upstream fetch. 1 credit charged on success.
- `fetched_at` — timestamp of when the cached record was originally collected, regardless of whether this specific request hit the cache.

Property schema is identical to the [by-address response](properties-by-address.md). Full field-level docs at [zillapi.com](https://zillapi.com/api/properties/).

## Errors

`400 invalid_zpid` · `401 invalid_api_key` · `402 out_of_credits` · `404 not_found` · `429 rate_limited` · `502 upstream_error`.

## Credit cost

**1 credit per fresh upstream fetch.** Cache hits are free.

Failed responses do not consume credits.

## See also

- [Full reference — `/properties/{zpid}`](https://zillapi.com/api/properties/)
- [Cache policy](https://zillapi.com/blog/zillow-api-caching/)
- [`examples/python/04_zestimate.py`](../examples/python/04_zestimate.py) — chains a by-address lookup into a zpid-based Zestimate fetch.
