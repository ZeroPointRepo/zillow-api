# Zillow API examples — Ruby

One runnable file using HTTParty. Ruby's `Net::HTTP` standard library works identically — the only reason to add HTTParty is the lighter syntax for query params and headers.

## Setup

Ruby 3.0 or later recommended.

```bash
bundle install
export ZILLAPI_KEY="zk_..."   # get one at https://zillapi.com/signup
```

If you'd rather avoid bundler, install the gem directly:

```bash
gem install httparty
```

## Run

```bash
bundle exec ruby lookup_property.rb
# or, if you installed the gem globally:
ruby lookup_property.rb
```

## Endpoint

| What | Endpoint | Cost |
|---|---|---|
| Look up by address | `GET /v1/properties/by-address` | 3 credits per success |

`HTTParty.get` returns a response object with `parsed_response` already decoded from JSON. The envelope is `{ "data": {...}, "request_id": "..." }` — index into `parsed_response["data"]` for the property record.
