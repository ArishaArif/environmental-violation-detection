from ultralytics import YOLO

model = YOLO("modelbest.pt")

# modelbest.pt class indices: 0 Auto-Rickshaw, 1 Bike, 2 Bus, 3 Car, 4 HCV, 5 LCV, 6 Toto, 7 Smoke
# Vehicle classes only (excludes Smoke):
results = model.track(
    source="sample.mp4",
    save=True,
    classes=[0, 1, 2, 3, 4, 5, 6],
    tracker="bytetrack.yaml"
)