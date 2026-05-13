# Contributing

This repository is a resource hub for the modern Zillow API — a curated README, language examples, endpoint stubs, and recipes. Pull requests are welcome.

## What we accept

- **New language examples** — Rust, Java, Kotlin, Swift, C#, Elixir, etc., following the existing folder pattern under `examples/`.
- **New recipes** — short walkthroughs (600–1,000 words) covering a specific real-world use case backed by working code.
- **Endpoint stub additions** — short reference pages under `endpoints/` summarizing endpoints not yet covered.
- **Fixes to existing examples** — bug fixes, field-name corrections, parameter updates when the API evolves.
- **Documentation improvements** — typo fixes, clearer prose, better tables.

## What we don't accept

- **A maintained SDK.** This repository is a resource hub, not a package. Don't add `pyproject.toml`, `package.json` for publishing, or any release tooling at the root.
- **Scrapers.** Every example calls the Zillapi REST API. Code that scrapes Zillow directly will be closed without review.
- **Marketing copy.** Keep prose technical and focused on the developer task at hand.
- **Emojis** in committed files.

## Ground rules

- Every example file must be runnable end-to-end with a real `ZILLAPI_KEY` env var. Walk through the snippet against the [OpenAPI spec](https://zillapi.com/openapi.json) before submitting.
- Match field names exactly — Property responses use `bedrooms`/`bathrooms`/`zestimate`/`address` (object); search rows use `beds`/`baths`/`address` (string). Do not mix them.
- Never commit credentials. The `ZILLAPI_KEY` environment variable is the only auth surface.
- Sign-off your commits (`git commit -s`).

## Local development

```bash
git clone https://github.com/nikhonit/zillow-api.git
cd zillow-api
export ZILLAPI_KEY="zk_..."

# Smoke-test a curl example
bash examples/curl/quickstart.sh

# Smoke-test the Python quickstart
cd examples/python && pip install -r requirements.txt && python 01_quickstart.py
```

## License

By contributing you agree that your contributions are licensed under the [MIT No Attribution](LICENSE) license.
