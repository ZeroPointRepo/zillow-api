# Zillow API examples — Go

One runnable file using `net/http` from the standard library. No third-party dependencies.

## Setup

Go 1.22 or later required.

```bash
export ZILLAPI_KEY="zk_..."   # get one at https://zillapi.com/signup
```

## Run

```bash
go run lookup_property.go
```

The struct-based unmarshal in `lookup_property.go` only decodes the fields it prints. If you need the full 300+ field record, change the inner struct to `map[string]any` or generate Go types from the [OpenAPI spec](https://zillapi.com/openapi.json) with a tool like `oapi-codegen`.

## Endpoint

| What | Endpoint | Cost |
|---|---|---|
| Look up by address | `GET /v1/properties/by-address` | 3 credits per success |

Failed responses (non-2xx) return the API error body in the `error` field of a wrapped `{error: {...}}` JSON envelope. The example surfaces the status code and the raw body.
