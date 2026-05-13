# Webhooks

Signed webhook deliveries for async job completions — useful when you submit a batch via `POST /v1/properties/batch` or `POST /v1/search/with-details` and don't want to poll `GET /v1/jobs/{id}` for status. The server signs each delivery with HMAC-SHA256 over the request body so receivers can verify the source.

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

**Response** — `201 Created` with the plaintext signing secret returned **once**. We store only the SHA-256 hash. If you lose the secret, revoke and re-create.

```json
{
  "data": {
    "id": "8c2a...",
    "url": "https://hooks.your-app.example.com/zillapi",
    "events": ["job.succeeded", "job.failed", "job.timed_out"],
    "active": true,
    "created_at": "2026-05-13T18:00:00Z",
    "secret": "whk_a1b2c3..."
  },
  "request_id": "..."
}
```

## List webhooks

`GET /v1/webhooks` — returns the array of registered webhooks for the key's account. The secret is omitted (we cannot recover it).

## Revoke a webhook

`DELETE /v1/webhooks/{id}` — `204 No Content` on success. Stops future deliveries within seconds. Historic deliveries remain queryable via `/deliveries`.

## Inspect deliveries

`GET /v1/webhooks/{id}/deliveries` — returns the last 200 attempted deliveries with status codes, retry counts, and response previews. Useful for debugging a receiver that's silently rejecting events.

## Event types

| Event | When |
|---|---|
| `job.succeeded` | Async job (batch detail, search-with-details, chained search) completed successfully. |
| `job.failed` | Job raised an upstream error. |
| `job.timed_out` | Job exceeded the platform timeout (default 30 minutes). |
| `job.aborted` | Job was cancelled by the caller. |

## Verifying the signature

Each delivery includes an `X-Zillapi-Signature` header with the HMAC-SHA256 of the raw request body using the secret returned at registration. Verify in Python:

```python
import hashlib, hmac

def verify(body_bytes, header_hex, secret):
    mac = hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, header_hex)
```

The delivery payload mirrors the [`Job` schema](https://zillapi.com/openapi.json) — `id`, `type`, `status`, `result_count`, `error`, `chain_stage`, plus timing fields. Fetch the actual results via `GET /v1/jobs/{id}/results` after receiving the `job.succeeded` event.

## Errors

`400 invalid_url` (non-HTTPS receiver) · `400 invalid_events` (unknown event in list) · `401 invalid_api_key` · `409 webhook_limit` (free-tier limit reached).

## Credit cost

**Webhook deliveries are free.** You pay for the underlying job (batch / search) but not for the notification fan-out.

## See also

- [Full reference — Webhooks](https://zillapi.com/api/webhooks/)
- [Webhook signature verification guide](https://zillapi.com/blog/zillow-api-webhook-verification/)
- [`/v1/jobs/{id}`](https://zillapi.com/api/jobs/) — the polling alternative when you don't want to host a receiver.
