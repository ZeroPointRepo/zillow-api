# Webhooks

Signed webhook deliveries for async job completions — useful when you submit a batch via `POST /v1/properties/batch` or `POST /v1/search/with-details` and don't want to poll `GET /v1/jobs/{id}` for status. The server signs each delivery with HMAC-SHA256 over `<timestamp>.<raw body>` so receivers can verify the source.

## Register a webhook

`POST /v1/webhooks`

```bash
curl -sS "https://api.zillapi.com/v1/webhooks" \
  -H "Authorization: Bearer $ZILLAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://hooks.your-app.example.com/zillapi",
    "events": ["job.succeeded", "job.failed", "job.timed_out"],
    "description": "Production batch sink"
  }'
```

**Response** — `201 Created` with the signing secret. We store the signing secret so we can sign deliveries. Keep your copy secure. If you lose the secret, revoke and re-create.

```json
{
  "data": {
    "id": "8c2a...",
    "url": "https://hooks.your-app.example.com/zillapi",
    "events": ["job.succeeded", "job.failed", "job.timed_out"],
    "active": true,
    "created_at": "2026-05-13T18:00:00Z",
    "secret": "whsec_AbCdEf..."
  },
  "request_id": "..."
}
```

## List webhooks

`GET /v1/webhooks` — returns the array of registered webhooks for the key's account. The secret is omitted from this list.

## Revoke a webhook

`DELETE /v1/webhooks/{id}` — `204 No Content` on success. Stops future deliveries within seconds. Historic deliveries remain queryable via `/deliveries`.

## Inspect deliveries

`GET /v1/webhooks/{id}/deliveries` — returns the last 50 attempted deliveries (up to 200 with `limit`) with status codes, retry counts, and response previews. Useful for debugging a receiver that's silently rejecting events.

## Event types

| Event | When |
|---|---|
| `job.succeeded` | Async job (batch detail, search-with-details, chained search) completed successfully. |
| `job.failed` | Job raised an upstream error. |
| `job.timed_out` | Job exceeded the platform timeout (default 30 minutes). |
| `job.aborted` | The job was aborted. |

## Verifying the signature

Each delivery includes `X-Zillow-Signature: t=<unix>,v1=<hex>`, the HMAC-SHA256 of `<t>.<raw body>` using the secret returned at registration. Verify in Python:

```python
import hashlib, hmac, re, time

def verify(body_bytes, header, secret):
    m = re.fullmatch(r"t=([0-9]{1,12}),v1=([0-9a-f]{64})", str(header))
    if not m:
        return False
    ts, sig = m.groups()
    if abs(time.time() - int(ts)) > 300:
        return False
    mac = hmac.new(secret.encode(), ts.encode() + b"." + body_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, sig)
```

`verify` returns `False` for a missing or malformed header, a wrong signature, or a timestamp more than 300 seconds from your clock.

The payload is `{ event, delivered_at, data: { job } }`; `job` has `id`, `type`, `status`, `result_count` and timing fields. Fetch the actual results via `GET /v1/jobs/{id}/results` after receiving the `job.succeeded` event.

## Errors

`400 invalid_url` (non-HTTPS receiver) · `400 invalid_event` (unknown event in list) · `401 invalid_api_key`.

## Credit cost

**Webhook deliveries are free.** You pay for the underlying job (batch / search) but not for the notification fan-out.

## See also

- [Full reference — Webhooks](https://zillapi.com/api/webhooks/)
- [Webhook signature verification guide](https://zillapi.com/recipes/verify-webhook/)
- [`/v1/jobs/{id}`](https://zillapi.com/api/jobs/) — the polling alternative when you don't want to host a receiver.
