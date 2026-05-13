# Zestimate sub-resource

`GET /v1/properties/{zpid}/zestimate`

Returns just the valuation fields — Zestimate, rent Zestimate, tax-assessed value, last-sold price — without the rest of the 300-field property record. Use this when you only need a valuation and want to avoid downloading the full record.

The Zestimate is also present as a top-level field on every Property response, so you don't strictly need this endpoint to read a Zestimate. The reasons to call the sub-resource directly are: smaller response payload, lower egress, and a dedicated cache key so it can be refreshed independently of the full record.

## Quick example

```bash
curl -s "https://api.zillapi.com/v1/properties/11026031/zestimate" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  | jq .data
```

```json
{
  "zestimate": 305100,
  "rent_zestimate": 1850,
  "tax_assessed_value": 248000,
  "last_sold_price": 211000,
  "currency": "USD"
}
```

## Parameters

| Name | In | Required | Type |
|---|---|---|---|
| `zpid` | path | yes | string (numeric) |

No query parameters.

## Response

Envelope: `{ "data": {...}, "request_id": "..." }`.

**Note the naming convention.** The sub-resource uses snake_case (`rent_zestimate`, `tax_assessed_value`, `last_sold_price`), while the top-level Property record uses camelCase (`rentZestimate`, `taxAssessedValue`). This is consistent with the [OpenAPI spec](https://zillapi.com/openapi.json) — the sub-resource was added later with a different convention and we left it that way to avoid breaking callers.

| Field | Type | Notes |
|---|---|---|
| `zestimate` | number / null | The Zestimate. `null` for properties without a published valuation. |
| `rent_zestimate` | number / null | Estimated rent. |
| `tax_assessed_value` | number / null | Most recent tax-assessed value. |
| `last_sold_price` | number / null | Last recorded sale price. |
| `currency` | string | Always `USD` in the current API. |

## Errors

`400 invalid_zpid` · `401 invalid_api_key` · `402 out_of_credits` · `404 not_found` (no zestimate available for this property) · `429 rate_limited`.

## Credit cost

**1 credit per successful call.** Cache hits are free.

Failed responses do not consume credits.

## See also

- [Full reference — Zestimate sub-resource](https://zillapi.com/api/properties/#zestimate)
- [Zestimate accuracy notes](https://www.zillow.com/z/zestimate/) (Zillow Group)
- [`examples/python/04_zestimate.py`](../examples/python/04_zestimate.py) — end-to-end address-to-Zestimate workflow.
- [`recipes/pandas-zestimate-batch.md`](../recipes/pandas-zestimate-batch.md) — batch valuations into a DataFrame.
