# Security policy

## Reporting a vulnerability

Email **nikhil@landkit.pro** with the subject line `SECURITY: zillow-api`. Please do not open public GitHub issues for security reports.

We will acknowledge receipt within 72 hours and aim to publish a fix or mitigation within 14 days for confirmed issues.

## Scope

This repository contains documentation and code examples for the [Zillapi REST API](https://zillapi.com). It is a resource hub, not a runtime service. Security-relevant surfaces:

- **Example code** — six language folders under `examples/`. If you find a snippet that mishandles credentials, fails open on errors, or demonstrates an unsafe pattern, please report it.
- **Documentation accuracy** — endpoint stubs and recipes that recommend insecure practices (hardcoding keys, disabling TLS verification, ignoring error responses) are in scope.
- **Supply chain** — the example dependencies are minimal (`httpx` for Python, `httparty` for Ruby, native `fetch` for Node, `net/http` stdlib for Go). Vulnerabilities in those upstream packages should be reported to the package maintainers, but please flag them here too so we can pin or replace the dependency.

For vulnerabilities in the **Zillapi service itself** (auth, billing, data exposure), report directly to the email above with the subject line `SECURITY: zillapi-service`.

## Credential handling in examples

Every example reads the API key from the `ZILLAPI_KEY` environment variable. No example writes the key to disk, logs it, or hardcodes it. Example code:

- Reads `ZILLAPI_KEY` from the environment at call time.
- Sends it only over HTTPS to `https://api.zillapi.com`.
- Does not retry indefinitely on auth failures.

If you find an example that violates any of those properties, that is a vulnerability — please report it.

## Trademark

Zillapi is an independent service and is not affiliated with, endorsed by, or sponsored by Zillow Group, Inc.
