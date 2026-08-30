import cv2
import os
import csv
import argparse
import requests
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from ultralytics import YOLO
from anpr_engine import extract_plate_data

# Load environment variables from the .env file[span_2](start_span)[span_2](end_span)
load_dotenv()

# Configuration[span_3](start_span)[span_3](end_span)
API_URL = "http://127.0.0.1:8000/incidents/"

# Uses your .env variable for the demo, but falls back to your local Desktop folder for testing[span_4](start_span)[span_4](end_span)
EVIDENCE_DIR = os.getenv("EVIDENCE_SAVE_PATH", r"C:\Users\user\OneDrive\Desktop\evidence_crops")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# 1. Load local YOLOv8 model globally 
# Renamed to match your updated folder structure
model = YOLO('plate_detector.pt')

# --- Collaborator's CSV Helper Functions ---[span_5](start_span)[span_5](end_span)
def load_vehicle_boxes(path):
    frames = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["is_vehicle"] not in ("True", "true", "1"):
                continue
            frames[int(row["frame"])].append({
                "track_id": int(row["track_id"]),
                "x1": float(row["x1"]), "y1": float(row["y1"]),
                "x2": float(row["x2"]), "y2": float(row["y2"]),
            })
    return frames

def load_candidates(path):
    candidates = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            candidates.append({
                "vehicle_track_id": int(row["vehicle_track_id"]),
                "first_seen_frame": int(row["first_seen_frame"]),
                "diverge_frame": int(row["diverge_frame"]),
                "lifetime_frames": int(row["lifetime_frames"]),
            })
    return candidates

def vehicle_box_at(vehicle_frames, frame_idx, track_id):
    for v in vehicle_frames.get(frame_idx, []):
        if v["track_id"] == track_id:
            return v
    return None

def confidence_from_candidate(c):
    return round(min(0.9, 0.5 + c["lifetime_frames"] / 40), 2)
# ---------------------------------------------

def process_video_incidents(source_video, boxes_csv, candidates_csv, violation_type="littering", location_lat=31.0217, location_lng=73.8532):
    # Load upstream motion tracking data[span_6](start_span)[span_6](end_span)
    vehicle_frames = load_vehicle_boxes(boxes_csv)
    candidates = load_candidates(candidates_csv)

    if not candidates:
        print("No candidates found in CSV.")
        return

    cap = cv2.VideoCapture(source_video)
    reported = 0

    for c in candidates:
        # Jump directly to the divergence frame[span_7](start_span)[span_7](end_span)
        target_frame = c["diverge_frame"]
        veh_box = vehicle_box_at(vehicle_frames, target_frame, c["vehicle_track_id"])
        
        if veh_box is None:
            continue

        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ok, frame = cap.read()
        if not ok:
            continue

        # 2. Detect Plate via offline YOLOv8 on the FULL frame[span_8](start_span)[span_8](end_span)
        print(f"Running YOLO inference on frame {target_frame}...")
        results = model(frame)
        
        if len(results[0].boxes) == 0:
            print("No plates detected in the frame.")
            continue

        # 3. Spatial Matching logic
        target_plate_box = None
        veh_x1, veh_y1, veh_x2, veh_y2 = veh_box["x1"], veh_box["y1"], veh_box["x2"], veh_box["y2"]
        
        for box in results[0].boxes:
            px1, py1, px2, py2 = map(int, box.xyxy[0])
            # Find center of the detected plate
            pcx, pcy = (px1 + px2) / 2, (py1 + py2) / 2 
            
            # Check if the plate's center falls inside the vehicle's bounding box coordinates
            if veh_x1 <= pcx <= veh_x2 and veh_y1 <= pcy <= veh_y2:
                # If multiple plates map to one car, grab the highest confidence one
                if target_plate_box is None or box.conf[0] > target_plate_box.conf[0]:
                    target_plate_box = box
                    
        if target_plate_box is None:
            print(f"No plate geometrically matched to violating vehicle {c['vehicle_track_id']}.")
            continue

        # 4. Crop and Save Evidence (YOLO returns xyxy format)[span_9](start_span)[span_9](end_span)
        px1, py1, px2, py2 = map(int, target_plate_box.xyxy[0])
        crop_img = frame[py1:py2, px1:px2]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_filename = f"violation_{timestamp}.jpg"
        evidence_fullpath = os.path.join(EVIDENCE_DIR, evidence_filename)
        cv2.imwrite(evidence_fullpath, crop_img)

        # 5. Extract Text & Confidence via Reusable Module[span_10](start_span)[span_10](end_span)
        plate_data = extract_plate_data(crop_img)

        # 6. Build and Send JSON Payload[span_11](start_span)[span_11](end_span)
        payload = {
            "violation_type": violation_type,
            "confidence": confidence_from_candidate(c), # Replaced YOLO conf with motion tracking conf[span_12](start_span)[span_12](end_span)[span_13](start_span)[span_13](end_span)
            "plate_number": plate_data["plate_number"],
            "plate_confidence": plate_data["plate_confidence"],
            "location_lat": location_lat, # Retained your custom coordinates[span_14](start_span)[span_14](end_span)
            "location_lng": location_lng,
            "evidence_path": evidence_filename
        }

        try:
            api_response = requests.post(API_URL, json=payload)
            if api_response.status_code == 201:
                print(f"Success! Incident logged for plate {plate_data['plate_number']} (Conf: {plate_data['plate_confidence']})")
                reported += 1
            else:
                print(f"Backend API Error {api_response.status_code}: {api_response.text}")
        except requests.exceptions.ConnectionError:
            print("Connection refused. Is Uvicorn running on port 8000?")

    cap.release()
    print(f"\nBatch processing complete! Reported {reported}/{len(candidates)} candidate(s).")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Original video, e.g. sample.mp4")
    parser.add_argument("--boxes", default="boxes.csv")
    parser.add_argument("--candidates", default="candidates.csv")
    args = parser.parse_args()

    process_video_incidents(args.source, args.boxes, args.candidates)
