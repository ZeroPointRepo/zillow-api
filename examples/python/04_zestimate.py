"""Dedicated Zestimate sub-resource.

`/v1/properties/{zpid}/zestimate` returns only the valuation fields — Zestimate,
rent Zestimate, tax-assessed value, last-sold price — without the rest of the
300-field property record. Useful when you want valuations only.

Note: the sub-resource uses snake_case (`rent_zestimate`, `tax_assessed_value`,
`last_sold_price`), while the top-level property record uses camelCase
(`rentZestimate`, `taxAssessedValue`). This is consistent with the OpenAPI
spec — the sub-resource was added later with a different naming convention.

Run:
    export ZILLAPI_KEY="zk_..."
    python 04_zestimate.py
"""
import os

import httpx

KEY = os.environ["ZILLAPI_KEY"]
ADDRESS = "17 Zelma Dr, Greenville, SC 29617"

with httpx.Client(
    base_url="https://api.zillapi.com",
    headers={"Authorization": f"Bearer {KEY}"},
    timeout=30,
) as client:
    # Step 1: resolve the address to a zpid (3 credits, fields=zpid keeps it cheap).
    lookup = client.get(
        "/v1/properties/by-address",
        params={"address": ADDRESS, "fields": "zpid"},
    )
    lookup.raise_for_status()
    zpid = lookup.json()["data"]["zpid"]

    # Step 2: hit the dedicated Zestimate endpoint (1 credit, cache-friendly).
    zest = client.get(f"/v1/properties/{zpid}/zestimate")
    zest.raise_for_status()

data = zest.json()["data"]
print(f"Address:           {ADDRESS}")
print(f"zpid:              {zpid}")
print(f"Zestimate:         ${data['zestimate']:,}" if data.get("zestimate") else "Zestimate:         n/a")
print(f"Rent Zestimate:    ${data['rent_zestimate']:,}" if data.get("rent_zestimate") else "Rent Zestimate:    n/a")
print(f"Tax-assessed:      ${data['tax_assessed_value']:,}" if data.get("tax_assessed_value") else "Tax-assessed:      n/a")
print(f"Last-sold:         ${data['last_sold_price']:,}" if data.get("last_sold_price") else "Last-sold:         n/a")
