#!/usr/bin/env bash
# Address lookup with field projection. Smaller response payload = smaller tokens
# if you're piping the JSON to an LLM, and faster transport over slow networks.
#
# Usage:
#   bash lookup_by_address.sh "350 5th Ave, New York, NY 10118"

set -euo pipefail

: "${ZILLAPI_KEY:?Set ZILLAPI_KEY env var: export ZILLAPI_KEY=zk_...}"
ADDRESS="${1:-350 5th Ave, New York, NY 10118}"

# `fields` is a comma-separated dotted-path projection. Server trims the response
# before sending. Use this when you don't need the full 300+ field record.
FIELDS="zpid,address,price,zestimate,rentZestimate,bedrooms,bathrooms,livingArea,yearBuilt,homeType,homeStatus,taxAssessedValue"

curl -sS "https://api.zillapi.com/v1/properties/by-address" \
  -G \
  --data-urlencode "address=$ADDRESS" \
  --data-urlencode "fields=$FIELDS" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  | jq .
