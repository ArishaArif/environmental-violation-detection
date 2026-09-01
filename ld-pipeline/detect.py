from ultralytics import YOLO

model = YOLO("vehicle_detector.pt")

# vehicle_detector.pt's classes: 0 Auto-Rickshaw, 1 Bike, 2 Bus, 3 Car,
# 4 HCV, 5 LCV, 6 Toto, 7 Smoke. Classes 0-6 = vehicles only; 7 (Smoke) is
# deliberately excluded — this pass is littering-only, no smoke detection.
results = model.track(
    source="sample.mp4",
    save=True,
    classes=[0, 1, 2, 3, 4, 5, 6],
    tracker="bytetrack.yaml"
)