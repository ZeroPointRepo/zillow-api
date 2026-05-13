// Bounding-box search for active for-sale listings.
//
// `/v1/listings` (GET) accepts a comma-separated `bbox` string in decimal
// degrees ("west,south,east,north"). The bbox below covers central San
// Francisco.
//
// Search results use a different field shape than property detail records:
// `address` is a string, `beds`/`baths` (not `bedrooms`/`bathrooms`),
// `unformattedPrice` is the integer.
//
// Run:
//   export ZILLAPI_KEY="zk_..."
//   node 03_search_listings.mjs

const KEY = process.env.ZILLAPI_KEY;
if (!KEY) {
  console.error("Set ZILLAPI_KEY env var: export ZILLAPI_KEY=zk_...");
  process.exit(1);
}

const url = new URL("https://api.zillapi.com/v1/listings");
url.searchParams.set("status", "for_sale");
url.searchParams.set("bbox", "-122.45,37.74,-122.40,37.79");
url.searchParams.set("price_min", "800000");
url.searchParams.set("price_max", "2000000");
url.searchParams.set("beds_min", "2");
url.searchParams.set("home_types", "house,condo,townhouse");
url.searchParams.set("max_items", "20");

const resp = await fetch(url, {
  headers: { Authorization: `Bearer ${KEY}` },
});

if (!resp.ok) {
  throw new Error(`HTTP ${resp.status}: ${await resp.text()}`);
}

const { data } = await resp.json();
console.log(`Found ${data.length} listings\n`);

for (const row of data) {
  const price = row.unformattedPrice
    ? `$${row.unformattedPrice.toLocaleString()}`
    : row.price ?? "n/a";
  console.log(
    `  ${(row.address ?? "?").padEnd(40)}  ${price.padStart(12)}  ` +
      `${row.beds ?? "?"}bd/${row.baths ?? "?"}ba  ${row.area?.toLocaleString() ?? "?"} sqft`
  );
}
