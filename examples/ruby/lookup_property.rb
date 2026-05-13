# Quickstart: look up one property by address and print the Zestimate.
#
# Run:
#   bundle install
#   export ZILLAPI_KEY="zk_..."
#   bundle exec ruby lookup_property.rb

require "httparty"
require "json"

KEY = ENV.fetch("ZILLAPI_KEY") do
  abort("Set ZILLAPI_KEY env var: export ZILLAPI_KEY=zk_...")
end

ADDRESS = ARGV.first || "1600 Pennsylvania Ave NW, Washington DC 20500"

resp = HTTParty.get(
  "https://api.zillapi.com/v1/properties/by-address",
  query: { address: ADDRESS },
  headers: { "Authorization" => "Bearer #{KEY}" },
  timeout: 30
)

unless resp.success?
  abort("HTTP #{resp.code}: #{resp.body}")
end

prop = resp.parsed_response["data"]
addr = prop["address"]

def with_commas(n)
  n ? n.to_i.to_s.gsub(/(\d)(?=(\d{3})+$)/, '\1,') : "n/a"
end

puts "#{addr['streetAddress']}, #{addr['city']}, #{addr['state']} #{addr['zipcode']}"
puts "zpid:        #{prop['zpid']}"
puts "Zestimate:   $#{with_commas(prop['zestimate'])}"
puts "Beds/baths:  #{prop['bedrooms']}/#{prop['bathrooms']}"
puts "Living area: #{with_commas(prop['livingArea'])} sqft"
puts "Year built:  #{prop['yearBuilt']}"
