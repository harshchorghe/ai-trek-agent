import time
from tools.db import normalize_destination, get_cached_item, save_cached_item, get_popular_destinations, mongo_available

print("[Diagnostics] EXPLORUSH KNOWLEDGE BASE TEST SUITE")
print("=======================================")

# Test 1: Normalization
print("\nTest 1: Normalizing Destinations")
variations = ["Goa ", "Mount Abu", "Ujjain Junction", "jaipur-city", "MUMBAI beach/"]
for v in variations:
    norm = normalize_destination(v)
    print(f"  '{v}' -> '{norm}'")

# Test 2: Save and Load Cache
print("\nTest 2: Cache Save & Load (Permanent Asset)")
test_dest = "Jaipur"
save_cached_item("hotel_mid-range", test_dest, "Taj Rambagh Palace, Bloom Suites, Zostel Jaipur", source="test-runner")

cached_val = get_cached_item("hotel_mid-range", test_dest)
print(f"  Saved & loaded hotel_mid-range for {test_dest}: {cached_val}")

# Test 3: Expiry Policy (Weather)
print("\nTest 3: Expiry Policy (Weather - Short Expiry)")
save_cached_item("weather", test_dest, "Sunny, 28C, humidity 60%", source="test-runner")
weather_val = get_cached_item("weather", test_dest)
print(f"  Initial weather load: {weather_val}")

# Test 4: Hit tracking & Analytics
print("\nTest 4: Hit Tracking & Popular destinations")
# Trigger a few more hits
get_cached_item("hotel_mid-range", test_dest)
get_cached_item("hotel_mid-range", test_dest)

popular = get_popular_destinations(limit=3)
print("  Popular Destinations Ranking:")
for idx, item in enumerate(popular, 1):
    print(f"    {idx}. {item.get('destination')} (Hits: {item.get('totalHits')})")

print("\n=======================================")
print("[Diagnostics] Completed successfully!")
