// Quickstart: look up one property and print the Zestimate.
//
// Run:
//   export ZILLAPI_KEY="zk_..."
//   node 01_quickstart.mjs

const KEY = process.env.ZILLAPI_KEY;
if (!KEY) {
  console.error("Set ZILLAPI_KEY env var: export ZILLAPI_KEY=zk_...");
  process.exit(1);
}

const url = new URL("https://api.zillapi.com/v1/properties/by-address");
url.searchParams.set("address", "1600 Pennsylvania Ave NW, Washington DC 20500");

const resp = await fetch(url, {
  headers: { Authorization: `Bearer ${KEY}` },
});

if (!resp.ok) {
  const detail = await resp.text();
  throw new Error(`HTTP ${resp.status}: ${detail}`);
}

const { data } = await resp.json();
const a = data.address;

console.log(`${a.streetAddress}, ${a.city}, ${a.state} ${a.zipcode}`);
console.log(`zpid:        ${data.zpid}`);
console.log(`Zestimate:   ${data.zestimate ? `$${data.zestimate.toLocaleString()}` : "n/a"}`);
console.log(`Beds/baths:  ${data.bedrooms}/${data.bathrooms}`);
console.log(`Living area: ${data.livingArea?.toLocaleString() ?? "n/a"} sqft`);
console.log(`Year built:  ${data.yearBuilt}`);
