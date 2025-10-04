#!/bin/bash

# UBEC API Testing Suite - V2 API Edition
# Tests the phenomenological observation system endpoints

API_BASE="http://localhost:8000"
TIMESTAMP=$(date +%s)
TEST_DEVICE="TEST_DEVICE_${TIMESTAMP}"
RESPONSE_FILE="/tmp/api_test_response_${TIMESTAMP}.json"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_num=$1
    local test_name="$2"
    local method="$3"
    local endpoint="$4"
    local data="$5"
    local expected_status=$6
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo ""
    echo "[Test ${test_num}] ${test_name}"
    echo "----------------------------------------"
    echo "Endpoint: ${method} ${endpoint}"
    
    if [ -n "$data" ]; then
        echo "Data: ${data}"
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "${method}" "${API_BASE}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "${data}")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "${method}" "${API_BASE}${endpoint}")
    fi
    
    # Split response and status code
    STATUS_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    echo "Status: ${STATUS_CODE}"
    echo "Response:"
    echo "${BODY}" | python3 -m json.tool 2>/dev/null || echo "${BODY}"
    
    if [ "${STATUS_CODE}" -eq "${expected_status}" ]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAILED (expected ${expected_status}, got ${STATUS_CODE})${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Start tests
echo ""
echo "================================================================"
echo "UBEC API TESTING SUITE - V2 API"
echo "================================================================"
echo "Testing API at: ${API_BASE}"
echo "Date: $(date)"
echo ""

# Section 1: Health & System Status
echo "================================================================"
echo "SECTION 1: HEALTH & SYSTEM CHECKS"
echo "================================================================"

run_test 1 "API Health Check" "GET" "/health" "" 200

run_test 2 "API Root Endpoint" "GET" "/" "" 200

run_test 3 "System Status" "GET" "/status" "" 200

run_test 4 "V2 Test Endpoint" "GET" "/api/v2/test" "" 200

run_test 5 "V2 Health Check" "GET" "/api/v2/health" "" 200

# Section 2: System Statistics
echo ""
echo "================================================================"
echo "SECTION 2: SYSTEM STATISTICS"
echo "================================================================"

run_test 6 "Get System Statistics" "GET" "/api/v2/system/stats" "" 200

# Section 3: Observer Registration
echo ""
echo "================================================================"
echo "SECTION 3: OBSERVER REGISTRATION"
echo "================================================================"

OBSERVER_DATA=$(cat <<EOF
{
  "observer_type": "environmental_sensor",
  "external_identity": {
    "device_id": "${TEST_DEVICE}",
    "serial_number": "SN${TIMESTAMP}"
  },
  "gesture": {
    "location": {
      "lat": 52.3,
      "lon": 14.5
    },
    "capabilities": ["temperature", "humidity", "pressure"],
    "device_wallet": "GBXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  }
}
EOF
)

run_test 7 "Register Observer" "POST" "/api/v2/observers/register" "$OBSERVER_DATA" 200

# Section 4: Phenomenon Creation
echo ""
echo "================================================================"
echo "SECTION 4: PHENOMENON CREATION"
echo "================================================================"

PHENOMENON_DATA=$(cat <<EOF
{
  "moment": "2025-10-02T12:00:00Z",
  "gesture": {
  }
}
EOF
)

run_test 8 "Create Phenomenon" "POST" "/api/v2/phenomena/create" "$PHENOMENON_DATA" 200

run_test 9 "Get Active Phenomena" "GET" "/api/v2/phenomena/active" "" 200

# Section 5: Observation Creation
echo ""
echo "================================================================"
echo "SECTION 5: OBSERVATION CREATION"
echo "================================================================"

# Note: This would need actual observer_id and phenomenon_id from previous tests
# For now, we'll show the expected structure

OBSERVATION_DATA=$(cat <<EOF
{
  "observer_id": "00000000-0000-0000-0000-000000000000",
  "phenomenon_id": "00000000-0000-0000-0000-000000000000",
  "perception": {
    "measurement_value": 22.5,
    "measurement_unit": "celsius",
    "sensor_reading": 22.5
  },
  "attention_quality": 0.95,
  "clarity": 0.90
}
EOF
)

echo ""
echo "[Test 10] Create Observation (Example Structure Only)"
echo "----------------------------------------"
echo "Note: This requires valid observer_id and phenomenon_id from DB"
echo "Example structure:"
echo "$OBSERVATION_DATA" | python3 -m json.tool
echo -e "${YELLOW}⚠️  SKIPPED (requires database IDs)${NC}"

# Section 6: Pattern Detection
echo ""
echo "================================================================"
echo "SECTION 6: PATTERN DETECTION & QUERIES"
echo "================================================================"

run_test 11 "Get Emerging Patterns" "GET" "/api/v2/patterns/emerging" "" 200

LOCATION_QUERY="/api/v2/patterns/at-location?lat=52.3&lon=14.5&radius_km=10&days=30"
run_test 12 "Get Location Patterns" "GET" "$LOCATION_QUERY" "" 200

# Section 7: Gift Economy
echo ""
echo "================================================================"
echo "SECTION 7: GIFT ECONOMY"
echo "================================================================"

GIFT_DATA=$(cat <<EOF
{
  "giver_id": "00000000-0000-0000-0000-000000000000",
  "gift_type": "observation",
  "ubec_expression": 7.14
}
EOF
)

echo ""
echo "[Test 13] Offer Gift (Example Structure Only)"
echo "----------------------------------------"
echo "Note: This requires valid observer_id from DB"
echo "Example structure:"
echo "$GIFT_DATA" | python3 -m json.tool
echo -e "${YELLOW}⚠️  SKIPPED (requires database IDs)${NC}"

# Section 8: Learning Journeys
echo ""
echo "================================================================"
echo "SECTION 8: LEARNING JOURNEYS"
echo "================================================================"

JOURNEY_DATA=$(cat <<EOF
{
  "observer_id": "00000000-0000-0000-0000-000000000000",
  "journey_type": "environmental_monitoring",
  "starting_intention": "Learn to observe temperature patterns"
}
EOF
)

echo ""
echo "[Test 14] Start Learning Journey (Example Structure Only)"
echo "----------------------------------------"
echo "Note: This requires valid observer_id from DB"
echo "Example structure:"
echo "$JOURNEY_DATA" | python3 -m json.tool
echo -e "${YELLOW}⚠️  SKIPPED (requires database IDs)${NC}"

# Final Summary
echo ""
echo "================================================================"
echo "TEST SUMMARY"
echo "================================================================"
echo ""
echo "Total Tests:  ${TOTAL_TESTS}"
echo "Passed:       ${PASSED_TESTS}"
echo "Failed:       ${FAILED_TESTS}"
echo ""

if [ ${FAILED_TESTS} -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo ""
    echo "Review the failed tests above."
    echo "Common issues:"
    echo "  - API not running"
    echo "  - Database not configured"
    echo "  - Endpoints not implemented"
    echo ""
    exit 1
fi
