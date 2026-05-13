#!/usr/bin/env bash
# Quickstart: look up a U.S. property and print its zpid, address, and Zestimate.
# Get a free key (100 credits, no card) at https://zillapi.com/signup

set -euo pipefail

: "${ZILLAPI_KEY:?Set ZILLAPI_KEY env var: export ZILLAPI_KEY=zk_...}"
ADDRESS="${1:-1600 Pennsylvania Ave NW, Washington DC 20500}"

curl -s "https://api.zillapi.com/v1/properties/by-address" \
  -G --data-urlencode "address=$ADDRESS" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  | jq '.data | {zpid, address, zestimate, rentZestimate, bedrooms, bathrooms, livingArea, yearBuilt}'
