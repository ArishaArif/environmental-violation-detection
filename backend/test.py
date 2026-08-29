import requests

BASE = "http://127.0.0.1:8000"

print("1. Testing missing required field...")
r = requests.post(f"{BASE}/incidents/", json={"confidence": 0.8})
print(f"   Status: {r.status_code} (expecting 422) — {'PASS' if r.status_code == 422 else 'FAIL'}")

print("2. Testing wrong data type...")
r = requests.post(f"{BASE}/incidents/", json={"violation_type": "littering", "confidence": "high"})
print(f"   Status: {r.status_code} (expecting 422) — {'PASS' if r.status_code == 422 else 'FAIL'}")

print("3. Testing valid incident creation...")
r = requests.post(f"{BASE}/incidents/", json={
    "violation_type": "littering",
    "confidence": 0.85,
    "plate_number": "TEST-001",
    "plate_confidence": 0.7,
    "location_lat": 31.5204,
    "location_lng": 74.3587,
})
print(f"   Status: {r.status_code} (expecting 201) — {'PASS' if r.status_code == 201 else 'FAIL'}")

print("4. Testing nonexistent incident lookup...")
r = requests.get(f"{BASE}/incidents/999999")
print(f"   Status: {r.status_code} (expecting 404) — {'PASS' if r.status_code == 404 else 'FAIL'}")

print("\nDone. If all say PASS, your API handles errors correctly — Day 4 hardening is complete.")