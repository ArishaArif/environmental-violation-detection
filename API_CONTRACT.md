# API Contract — Environmental Violation Detection Backend

Base URL: http://127.0.0.1:8000

## POST /incidents/
Creates a new incident. Used by the CV/ANPR pipeline.

Request body:
{
  "violation_type": "littering",
  "confidence": 0.85,
  "plate_number": "LEA-1234",      // optional, null if no plate
  "plate_confidence": 0.75,         // optional, null if no plate
  "location_lat": 31.5204,          // optional
  "location_lng": 74.3587,          // optional
  "evidence_path": "frame_001.jpg"  // optional, filename only
}

Returns: 201 + the created incident object (includes generated "id", "timestamp", "review_status": "pending")

## GET /incidents/
Lists incidents. Supports filters: ?violation_type=littering&review_status=pending&skip=0&limit=50

## GET /incidents/{id}
Returns one incident by id. 404 if not found.

## PATCH /incidents/{id}
Updates review_status and/or notes.
Body: { "review_status": "accepted" }
Allowed review_status values: pending, accepted, rejected, needs_investigation

## GET /analytics/
Returns: { total_incidents, pending_review, by_type, by_day, by_hotspot }

## Errors
All errors return: { "error": "message" } with standard HTTP status codes (404, 422, etc.)

## Evidence images
Every incident includes "evidence_url" — a full clickable link, ready for <img src>.
