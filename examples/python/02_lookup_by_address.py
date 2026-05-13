"""Look up a property with field projection.

The `fields` parameter is a comma-separated dotted-path projection. The server
trims the response before sending, which is useful when:

- you're piping the JSON to an LLM (smaller token bill),
- you only need a handful of fields and don't want to deserialize 300+.

Run:
    export ZILLAPI_KEY="zk_..."
    python 02_lookup_by_address.py "350 5th Ave, New York, NY 10118"
"""
import os
import sys

import httpx

KEY = os.environ["ZILLAPI_KEY"]
ADDRESS = sys.argv[1] if len(sys.argv) > 1 else "350 5th Ave, New York, NY 10118"

FIELDS = ",".join([
    "zpid",
    "address",
    "price",
    "zestimate",
    "rentZestimate",
    "bedrooms",
    "bathrooms",
    "livingArea",
    "yearBuilt",
    "homeType",
    "homeStatus",
    "taxAssessedValue",
])

with httpx.Client(
    base_url="https://api.zillapi.com",
    headers={"Authorization": f"Bearer {KEY}"},
    timeout=30,
) as client:
    resp = client.get(
        "/v1/properties/by-address",
        params={"address": ADDRESS, "fields": FIELDS},
    )

resp.raise_for_status()
prop = resp.json()["data"]

for key, value in prop.items():
    print(f"{key:20s} {value}")
