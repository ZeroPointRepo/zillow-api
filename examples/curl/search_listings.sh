#!/usr/bin/env bash
# Bounding-box search for active for-sale listings.
#
# /v1/listings is the GET-flavored search endpoint. `bbox` is a comma-separated
# string "west,south,east,north" in decimal degrees. The bbox below covers
# central San Francisco.
#
# Usage:
#   bash search_listings.sh

set -euo pipefail

: "${ZILLAPI_KEY:?Set ZILLAPI_KEY env var: export ZILLAPI_KEY=zk_...}"

BBOX="-122.45,37.74,-122.40,37.79"
PRICE_MIN=800000
PRICE_MAX=2000000
BEDS_MIN=2
HOME_TYPES="house,condo,townhouse"
MAX_ITEMS=20

curl -sS "https://api.zillapi.com/v1/listings" \
  -G \
  --data-urlencode "status=for_sale" \
  --data-urlencode "bbox=$BBOX" \
  --data-urlencode "price_min=$PRICE_MIN" \
  --data-urlencode "price_max=$PRICE_MAX" \
  --data-urlencode "beds_min=$BEDS_MIN" \
  --data-urlencode "home_types=$HOME_TYPES" \
  --data-urlencode "max_items=$MAX_ITEMS" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  | jq '.data[] | {zpid, address, unformattedPrice, beds, baths, area}'
