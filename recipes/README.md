# Recipes

Longer walkthroughs that combine multiple endpoints, library code, and operational patterns. Each recipe is self-contained — copy the code block, set `ZILLAPI_KEY`, and run.

| Recipe | What it covers | Endpoints |
|---|---|---|
| [pandas-zestimate-batch.md](pandas-zestimate-batch.md) | Pull Zestimates for hundreds of addresses into a pandas DataFrame, with sync concurrency and an async-batch fallback. | `/v1/properties/by-address`, `/v1/properties/batch` |
| [listing-alerts-cron.md](listing-alerts-cron.md) | Cron-based polling for new listings in a bounding box; diff against seen zpids; post to Slack/Discord. | `/v1/listings` |
| [multi-property-comparison.md](multi-property-comparison.md) | Pull a target property plus 3–5 comparables and render a side-by-side table. | `/v1/properties/by-address`, `/v1/properties/{zpid}/nearby`, `/v1/properties/{zpid}` |

If you have a recipe that you'd like to contribute, see [CONTRIBUTING.md](../CONTRIBUTING.md). Good recipes are 600–1,000 words, lead with a directly-answerable headline question, and include one complete working code block.
