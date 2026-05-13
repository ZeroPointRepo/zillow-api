"""Quickstart: look up one property and print the Zestimate.

Run:
    pip install -r requirements.txt
    export ZILLAPI_KEY="zk_..."
    python 01_quickstart.py
"""
import os

import httpx

KEY = os.environ["ZILLAPI_KEY"]
ADDRESS = "1600 Pennsylvania Ave NW, Washington DC 20500"

resp = httpx.get(
    "https://api.zillapi.com/v1/properties/by-address",
    params={"address": ADDRESS},
    headers={"Authorization": f"Bearer {KEY}"},
    timeout=30,
)
resp.raise_for_status()
prop = resp.json()["data"]

addr = prop["address"]
print(f"{addr['streetAddress']}, {addr['city']}, {addr['state']} {addr['zipcode']}")
print(f"zpid:        {prop['zpid']}")
print(f"Zestimate:   ${prop['zestimate']:,}" if prop.get("zestimate") else "Zestimate:   n/a")
print(f"Beds/baths:  {prop['bedrooms']}/{prop['bathrooms']}")
print(f"Living area: {prop['livingArea']:,} sqft")
print(f"Year built:  {prop['yearBuilt']}")
