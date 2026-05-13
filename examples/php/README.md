# Zillow API examples — PHP

One runnable file using PHP's `file_get_contents` with a stream context. No Composer dependencies — useful for shared hosting where you can't `composer install`.

## Setup

PHP 8.0 or later recommended. `allow_url_fopen` must be enabled (the default on most installs).

```bash
export ZILLAPI_KEY="zk_..."   # get one at https://zillapi.com/signup
```

If you'd rather use Guzzle, swap the `file_get_contents` block for `(new Client)->get(...)`. The response shape is identical.

## Run

```bash
php lookup_property.php
php lookup_property.php "350 5th Ave, New York, NY 10118"
```

## Endpoint

| What | Endpoint | Cost |
|---|---|---|
| Look up by address | `GET /v1/properties/by-address` | 3 credits per success |

The script returns a non-zero exit code on non-2xx responses, with the status and response body printed to stderr.
