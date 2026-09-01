# report_littering.py
# Glue script: reads candidates.csv (littering events) + boxes.csv (vehicle
# positions), grabs the vehicle crop at the moment of divergence, runs it
# through the ANPR module, and POSTs a real incident to the backend.

import argparse
import csv
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import cv2
import requests

# anpr_engine.py lives in ../ml-pipeline, not in this directory, so it isn't
# importable by default no matter where this script is run from. Add that
# folder to sys.path (relative to this file, not the current working
# directory) before importing it.
ML_PIPELINE_DIR = Path(__file__).resolve().parent.parent / "ml-pipeline"
if str(ML_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(ML_PIPELINE_DIR))

try:
    from anpr_engine import extract_plate_data
except ImportError as e:
    raise ImportError(
        f"Could not import anpr_engine from {ML_PIPELINE_DIR}. "
        "Make sure the ml-pipeline/ folder sits next to cv-pipeline/ in the "
        "repo, and that its dependencies (see ml-pipeline/requirements.txt) "
        "are installed in this environment."
    ) from e

API_URL = "http://127.0.0.1:8000/incidents/"

# The backend serves evidence images from backend/evidence/ (mounted at
# /evidence in main.py) and builds evidence_url from evidence_path relative
# to that folder. So files saved here MUST land in that exact folder, or the
# frontend's evidence thumbnails will 404. Resolved relative to this file
# (not the current working directory) so it works no matter where you run
# this script from — override with EVIDENCE_SAVE_PATH if you want somewhere
# else (e.g. a different backend instance on demo day).
EVIDENCE_DIR = os.getenv(
    "EVIDENCE_SAVE_PATH",
    str(Path(__file__).resolve().parent.parent / "backend" / "evidence"),
)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

DEFAULT_LOCATION = (31.5204, 74.3587)  # placeholder Lahore coords — swap if you have real ones


def load_vehicle_boxes(path):
    """frame -> list of vehicle rows (same shape as detect_littering.py's loader)"""
    frames = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["is_vehicle"] not in ("True", "true", "1"):
                continue
            frames[int(row["frame"])].append(
                {
                    "track_id": int(row["track_id"]),
                    "x1": float(row["x1"]), "y1": float(row["y1"]),
                    "x2": float(row["x2"]), "y2": float(row["y2"]),
                }
            )
    return frames


def load_candidates(path):
    candidates = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            candidates.append(
                {
                    "vehicle_track_id": int(row["vehicle_track_id"]),
                    "first_seen_frame": int(row["first_seen_frame"]),
                    "diverge_frame": int(row["diverge_frame"]),
                    "lifetime_frames": int(row["lifetime_frames"]),
                }
            )
    return candidates


def vehicle_box_at(vehicle_frames, frame_idx, track_id):
    for v in vehicle_frames.get(frame_idx, []):
        if v["track_id"] == track_id:
            return v
    return None


def confidence_from_candidate(c):
    """
    No ML confidence score exists for this heuristic method, so derive a
    rough proxy: longer-lived, cleanly tracked blobs score higher.
    Capped at 0.9 since this is a heuristic, not a trained classifier —
    be honest about that in the demo if asked.
    """
    return round(min(0.9, 0.5 + c["lifetime_frames"] / 40), 2)

def process(source_video, boxes_csv, candidates_csv, violation_type="littering"):
    vehicle_frames = load_vehicle_boxes(boxes_csv)
    candidates = load_candidates(candidates_csv)

    if not candidates:
        print("No candidates in candidates.csv — nothing to report.")
        return

    cap = cv2.VideoCapture(source_video)
    reported = 0

    for c in candidates:
        # Use the frame at divergence — that's the moment the object is
        # visibly separating from the vehicle, best evidence shot.
        target_frame = c["diverge_frame"]
        veh_box = vehicle_box_at(vehicle_frames, target_frame, c["vehicle_track_id"])
        if veh_box is None:
            print(f"Skipping candidate (no vehicle box at frame {target_frame})")
            continue

        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ok, frame = cap.read()
        if not ok:
            print(f"Could not read frame {target_frame}, skipping candidate.")
            continue

        x1, y1, x2, y2 = map(int, (veh_box["x1"], veh_box["y1"], veh_box["x2"], veh_box["y2"]))
        crop_img = frame[max(0, y1):y2, max(0, x1):x2]

        # Save evidence
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        evidence_filename = f"litter_{timestamp}.jpg"
        evidence_fullpath = os.path.join(EVIDENCE_DIR, evidence_filename)
        cv2.imwrite(evidence_fullpath, frame)  # full frame, more context than just the crop

        # Run ANPR on the vehicle crop
        plate_data = extract_plate_data(crop_img)

        payload = {
            "violation_type": violation_type,
            "confidence": confidence_from_candidate(c),
            "plate_number": plate_data["plate_number"],
            "plate_confidence": plate_data["plate_confidence"],
            "location_lat": DEFAULT_LOCATION[0],
            "location_lng": DEFAULT_LOCATION[1],
            "evidence_path": evidence_filename,
        }

        try:
            resp = requests.post(API_URL, json=payload)
            if resp.status_code == 201:
                print(f"Reported incident: plate={plate_data['plate_number']} "
                      f"conf={payload['confidence']} id={resp.json().get('id')}")
                reported += 1
            else:
                print(f"Backend error {resp.status_code}: {resp.text}")
        except requests.exceptions.ConnectionError:
            print("Connection refused — is uvicorn running on port 8000?")

    cap.release()
    print(f"\nDone. Reported {reported}/{len(candidates)} candidate(s) as incidents.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Original video, e.g. littering_sample.mp4")
    parser.add_argument("--boxes", default="boxes.csv")
    parser.add_argument("--candidates", default="candidates.csv")
    args = parser.parse_args()

    process(args.source, args.boxes, args.candidates) 
