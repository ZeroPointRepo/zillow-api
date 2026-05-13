"""Batch property lookups into a pandas DataFrame and write a CSV.

Pattern: loop through a list of addresses, hit `/v1/properties/by-address` for
each (with a `fields` projection to keep responses small), normalize into a
DataFrame, write CSV.

For larger batches (>100 addresses) prefer `POST /v1/properties/batch` and a
webhook callback over a sync loop — see `recipes/pandas-zestimate-batch.md`.

Run:
    pip install -r requirements.txt
    export ZILLAPI_KEY="zk_..."
    python 05_pandas_dataframe.py
"""
import os

import httpx
import pandas as pd

KEY = os.environ["ZILLAPI_KEY"]
ADDRESSES = [
    "17 Zelma Dr, Greenville, SC 29617",
    "350 5th Ave, New York, NY 10118",
    "1600 Pennsylvania Ave NW, Washington DC 20500",
    "1 Infinite Loop, Cupertino, CA 95014",
]
FIELDS = "zpid,address,price,zestimate,rentZestimate,bedrooms,bathrooms,livingArea,yearBuilt,homeType,homeStatus,taxAssessedValue"

rows = []
with httpx.Client(
    base_url="https://api.zillapi.com",
    headers={"Authorization": f"Bearer {KEY}"},
    timeout=30,
) as client:
    for addr in ADDRESSES:
        resp = client.get(
            "/v1/properties/by-address",
            params={"address": addr, "fields": FIELDS},
        )
        if resp.status_code != 200:
            print(f"  skip ({resp.status_code}): {addr}")
            continue
        rows.append(resp.json()["data"])

# `pd.json_normalize` flattens the nested address object into
# address.streetAddress / address.city / address.state / address.zipcode columns.
df = pd.json_normalize(rows)

print(f"\nLoaded {len(df)} properties. First rows:\n")
print(df[["zpid", "address.streetAddress", "zestimate", "bedrooms", "bathrooms", "livingArea"]].to_string(index=False))

out = "properties.csv"
df.to_csv(out, index=False)
print(f"\nWrote {out} ({len(df)} rows, {len(df.columns)} columns)")
