// Look up a property with a `fields` projection.
//
// The `fields` parameter trims the response server-side. Useful when:
//   - you're piping the JSON to an LLM (smaller token bill),
//   - you only need a handful of fields and don't want to deserialize 300+.
//
// Run:
//   export ZILLAPI_KEY="zk_..."
//   node 02_lookup_by_address.mjs "350 5th Ave, New York, NY 10118"

const KEY = process.env.ZILLAPI_KEY;
if (!KEY) {
  console.error("Set ZILLAPI_KEY env var: export ZILLAPI_KEY=zk_...");
  process.exit(1);
}

const address = process.argv[2] ?? "350 5th Ave, New York, NY 10118";

const FIELDS = [
  "zpid",
  "address",
  "price",
  "zestimate",
  "rentZestimate",
  "bedrooms",
  "bathrooms",
  "livingArea",
  "yearBuilt",
  "homeType",
  "homeStatus",
  "taxAssessedValue",
].join(",");

const url = new URL("https://api.zillapi.com/v1/properties/by-address");
url.searchParams.set("address", address);
url.searchParams.set("fields", FIELDS);

const resp = await fetch(url, {
  headers: { Authorization: `Bearer ${KEY}` },
});

if (!resp.ok) {
  throw new Error(`HTTP ${resp.status}: ${await resp.text()}`);
}

const { data } = await resp.json();
console.log(JSON.stringify(data, null, 2));
