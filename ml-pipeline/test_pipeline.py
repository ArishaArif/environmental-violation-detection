import cv2
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from ultralytics import YOLO
from anpr_engine import extract_plate_data

# Load environment variables from the .env file
load_dotenv()

# Configuration
API_URL = "http://127.0.0.1:8000/incidents/"

# Uses your .env variable for the demo, but falls back to your local Desktop folder for testing
EVIDENCE_DIR = os.getenv("EVIDENCE_SAVE_PATH", r"C:\Users\user\OneDrive\Desktop\evidence_crops")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# 1. Load local YOLOv8 model globally (Removed Roboflow configuration)
model = YOLO('best.pt')

def process_and_report_violation(image_path, violation_type="smoke", location_lat=31.0217, location_lng=73.8532):
    # Read Image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image at {image_path}")
        return

    # 2. Detect Plate via offline YOLOv8
    print("Running local YOLOv8 inference...")
    results = model(img)
    
    if len(results[0].boxes) == 0:
        print("No plates detected in the frame.")
        return

    # Get the bounding box with the highest confidence
    best_box = max(results[0].boxes, key=lambda x: x.conf[0])
    detection_conf = round(float(best_box.conf[0]), 2)
    
    # 3. Crop and Save Evidence (YOLO returns xyxy format)
    x1, y1, x2, y2 = map(int, best_box.xyxy[0])
    crop_img = img[y1:y2, x1:x2]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    evidence_filename = f"violation_{timestamp}.jpg"
    evidence_fullpath = os.path.join(EVIDENCE_DIR, evidence_filename)
    cv2.imwrite(evidence_fullpath, crop_img)

    # 4. Extract Text & Confidence via Reusable Module
    plate_data = extract_plate_data(crop_img)

    # 5. Build and Send JSON Payload (Strict Schema matching)
    payload = {
        "violation_type": violation_type,
        "confidence": detection_conf,
        "plate_number": plate_data["plate_number"],
        "plate_confidence": plate_data["plate_confidence"],
        "location_lat": location_lat,
        "location_lng": location_lng,
        "evidence_path": evidence_filename
        # review_status has been completely removed
    }

    try:
        api_response = requests.post(API_URL, json=payload)
        if api_response.status_code == 201:
            print(f"Success! Incident logged for plate {plate_data['plate_number']} (Conf: {plate_data['plate_confidence']})")
        else:
            print(f"Backend API Error {api_response.status_code}: {api_response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection refused. Is Uvicorn running on port 8000?")

if __name__ == "__main__":
    # Correct path applied directly to your ml-pipeline folder
    test_folder = r"C:\Users\user\OneDrive\Desktop\ml-pipeline\Pakistani-Number-plates.v1i.yolov8\test\images"
    
    print(f"Starting batch processing for folder: {test_folder}")
    
    for filename in os.listdir(test_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            full_image_path = os.path.join(test_folder, filename)
            print(f"\n--- Processing: {filename} ---")
            process_and_report_violation(full_image_path)
            
    print("\nBatch processing complete!")