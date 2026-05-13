// Quickstart: look up one property by address and print the Zestimate.
//
// Run:
//   export ZILLAPI_KEY="zk_..."
//   go run lookup_property.go
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
)

type Address struct {
	StreetAddress string `json:"streetAddress"`
	City          string `json:"city"`
	State         string `json:"state"`
	Zipcode       string `json:"zipcode"`
}

type Property struct {
	Zpid          string  `json:"zpid"`
	Address       Address `json:"address"`
	Price         float64 `json:"price"`
	Zestimate     float64 `json:"zestimate"`
	RentZestimate float64 `json:"rentZestimate"`
	Bedrooms      float64 `json:"bedrooms"`
	Bathrooms     float64 `json:"bathrooms"`
	LivingArea    float64 `json:"livingArea"`
	YearBuilt     int     `json:"yearBuilt"`
	HomeType      string  `json:"homeType"`
}

type Envelope struct {
	Data      Property `json:"data"`
	RequestID string   `json:"request_id"`
}

func main() {
	key := os.Getenv("ZILLAPI_KEY")
	if key == "" {
		log.Fatal("Set ZILLAPI_KEY env var: export ZILLAPI_KEY=zk_...")
	}

	u, _ := url.Parse("https://api.zillapi.com/v1/properties/by-address")
	q := u.Query()
	q.Set("address", "1600 Pennsylvania Ave NW, Washington DC 20500")
	u.RawQuery = q.Encode()

	req, _ := http.NewRequest("GET", u.String(), nil)
	req.Header.Set("Authorization", "Bearer "+key)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		log.Fatalf("request failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK {
		log.Fatalf("HTTP %d: %s", resp.StatusCode, string(body))
	}

	var env Envelope
	if err := json.Unmarshal(body, &env); err != nil {
		log.Fatalf("decode failed: %v", err)
	}

	p := env.Data
	a := p.Address
	fmt.Printf("%s, %s, %s %s\n", a.StreetAddress, a.City, a.State, a.Zipcode)
	fmt.Printf("zpid:        %s\n", p.Zpid)
	fmt.Printf("Zestimate:   $%.0f\n", p.Zestimate)
	fmt.Printf("Beds/baths:  %.0f/%.1f\n", p.Bedrooms, p.Bathrooms)
	fmt.Printf("Living area: %.0f sqft\n", p.LivingArea)
	fmt.Printf("Year built:  %d\n", p.YearBuilt)
}
