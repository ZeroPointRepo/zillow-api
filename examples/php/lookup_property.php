<?php
// Quickstart: look up one property by address and print the Zestimate.
//
// Run:
//   export ZILLAPI_KEY="zk_..."
//   php lookup_property.php
//   php lookup_property.php "350 5th Ave, New York, NY 10118"

declare(strict_types=1);

$key = getenv("ZILLAPI_KEY") ?: "";
if ($key === "") {
    fwrite(STDERR, "Set ZILLAPI_KEY env var: export ZILLAPI_KEY=zk_...\n");
    exit(1);
}

$address = $argv[1] ?? "1600 Pennsylvania Ave NW, Washington DC 20500";

$url = "https://api.zillapi.com/v1/properties/by-address?"
     . http_build_query(["address" => $address]);

$ctx = stream_context_create([
    "http" => [
        "method"        => "GET",
        "header"        => "Authorization: Bearer {$key}\r\n"
                         . "Accept: application/json\r\n",
        "timeout"       => 30,
        "ignore_errors" => true,
    ],
]);

$body = @file_get_contents($url, false, $ctx);
if ($body === false) {
    fwrite(STDERR, "Network error: " . (error_get_last()["message"] ?? "unknown") . "\n");
    exit(1);
}

// $http_response_header is auto-populated by the stream wrapper.
$status = 0;
if (isset($http_response_header[0]) && preg_match("#HTTP/[\d.]+\s+(\d+)#", $http_response_header[0], $m)) {
    $status = (int) $m[1];
}
if ($status !== 200) {
    fwrite(STDERR, "HTTP {$status}: {$body}\n");
    exit(1);
}

$envelope = json_decode($body, true, flags: JSON_THROW_ON_ERROR);
$prop = $envelope["data"];
$addr = $prop["address"];

printf("%s, %s, %s %s\n", $addr["streetAddress"], $addr["city"], $addr["state"], $addr["zipcode"]);
printf("zpid:        %s\n", $prop["zpid"]);
printf("Zestimate:   %s\n", isset($prop["zestimate"]) ? "\$" . number_format((float) $prop["zestimate"]) : "n/a");
printf("Beds/baths:  %s/%s\n", $prop["bedrooms"] ?? "?", $prop["bathrooms"] ?? "?");
printf("Living area: %s sqft\n", isset($prop["livingArea"]) ? number_format((float) $prop["livingArea"]) : "?");
printf("Year built:  %s\n", $prop["yearBuilt"] ?? "?");
