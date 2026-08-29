import requests, random

BASE = "http://127.0.0.1:8000/incidents/"
types = ["littering"]
statuses_test_plates = [f"LE{random.choice('ABCD')}-{random.randint(1000,9999)}" for _ in range(20)]

for plate in statuses_test_plates:
    requests.post(BASE, json={
        "violation_type": "littering",
        "confidence": round(random.uniform(0.5, 0.95), 2),
        "plate_number": plate,
        "plate_confidence": round(random.uniform(0.5, 0.9), 2),
        "location_lat": 31.5204 + random.uniform(-0.05, 0.05),
        "location_lng": 74.3587 + random.uniform(-0.05, 0.05),
    })

print("Seeded 20 test incidents.")