#!/bin/bash

# Test script for Property Scraper API
echo "=========================================="
echo "Property Scraper API Test Suite"
echo "=========================================="

API_URL="http://localhost:5001"

# Test 1: Health Check
echo -e "\n[TEST 1] Health Check"
echo "Request: GET $API_URL/health"
curl -s -X GET "$API_URL/health" | python3 -m json.tool
echo ""

# Test 2: GET request with Address header
echo -e "\n[TEST 2] GET /api/property with Address header"
echo "Request: GET $API_URL/api/property"
echo "Header: Address: Baker Street, London"
curl -s -X GET "$API_URL/api/property" \
  -H "Address: Baker Street, London" | python3 -m json.tool
echo ""

# Test 3: POST request with JSON body
echo -e "\n[TEST 3] POST /api/property with JSON body"
echo "Request: POST $API_URL/api/property"
curl -s -X POST "$API_URL/api/property" \
  -H "Content-Type: application/json" \
  -d '{"address": "Oxford Street, London"}' | python3 -m json.tool
echo ""

# Test 4: Batch request
echo -e "\n[TEST 4] POST /api/batch-properties"
echo "Request: POST $API_URL/api/batch-properties"
curl -s -X POST "$API_URL/api/batch-properties" \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Piccadilly Circus, London",
      "Leicester Square, London"
    ]
  }' | python3 -m json.tool
echo ""

# Test 5: Error handling - missing address
echo -e "\n[TEST 5] Error handling - missing address header"
echo "Request: GET $API_URL/api/property (no address)"
curl -s -X GET "$API_URL/api/property" | python3 -m json.tool
echo ""

echo "=========================================="
echo "All tests completed!"
echo "=========================================="
