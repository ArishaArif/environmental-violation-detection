import argparse
import csv
import json
from pathlib import Path

from ultralytics import YOLO

# Class NAMES (case-insensitive) that count as "vehicle" for the heuristic.
# Covers both COCO's names and best.pt's local vehicle-type names.
VEHICLE_NAMES = {
    "car", "truck", "bus", "motorcycle",              # COCO
    "auto-rickshaw", "bike", "hcv", "lcv", "toto",     # best.pt
}

# Class NAMES that count as a possible "litter object" proxy.
# Only meaningful for COCO-based models — best.pt has none of these,
# so the object side of the heuristic stays fully motion-based for it.
OBJECT_NAMES = {"bottle", "backpack", "handbag", "person"}


def extract(source: str, out_path: str, weights: str, conf: float = 0.25, imgsz: int = 640, tracker: str = "bytetrack.yaml"):
    model = YOLO(weights)

    # Resolve class IDs dynamically from the loaded model's actual names,
    # instead of assuming COCO's fixed indices.
    name_to_id = {name.lower(): idx for idx, name in model.names.items()}
    vehicle_ids = {name_to_id[n] for n in VEHICLE_NAMES if n in name_to_id}
    object_ids = {name_to_id[n] for n in OBJECT_NAMES if n in name_to_id}
    relevant_ids = sorted(vehicle_ids | object_ids)

    print(f"Loaded {weights} — {len(model.names)} classes.")
    print(f"Vehicle classes in use: {sorted(model.names[i] for i in vehicle_ids)}")
    print(f"Object classes in use: {sorted(model.names[i] for i in object_ids) or '(none — model has no object-proxy classes)'}")

    rows = []
    frame_idx = 0

    results_gen = model.track(
        source=source,
        classes=relevant_ids,
        tracker=tracker,
        conf=conf,
        imgsz=imgsz,
        persist=True,
        stream=True,
        verbose=False,
    )

    for result in results_gen:
        boxes = result.boxes
        if boxes is not None and boxes.id is not None:
            xyxy = boxes.xyxy.cpu().numpy()
            track_ids = boxes.id.cpu().numpy().astype(int)
            classes = boxes.cls.cpu().numpy().astype(int)
            confs = boxes.conf.cpu().numpy()

            for box, tid, cls, c in zip(xyxy, track_ids, classes, confs):
                x1, y1, x2, y2 = box
                rows.append(
                    {
                        "frame": frame_idx,
                        "track_id": int(tid),
                        "class_id": int(cls),
                        "class_name": model.names[int(cls)],
                        "is_vehicle": int(cls) in vehicle_ids,
                        "conf": round(float(c), 3),
                        "x1": round(float(x1), 1),
                        "y1": round(float(y1), 1),
                        "x2": round(float(x2), 1),
                        "y2": round(float(y2), 1),
                        "cx": round(float((x1 + x2) / 2), 1),
                        "cy": round(float((y1 + y2) / 2), 1),
                        "w": round(float(x2 - x1), 1),
                        "h": round(float(y2 - y1), 1),
                    }
                )
        frame_idx += 1

    out_path = Path(out_path)
    if out_path.suffix == ".json":
        with open(out_path, "w") as f:
            json.dump(rows, f, indent=2)
    else:
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "frame", "track_id", "class_id", "class_name", "is_vehicle",
                    "conf", "x1", "y1", "x2", "y2", "cx", "cy", "w", "h",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)

    print(f"Wrote {len(rows)} box records across {frame_idx} frames -> {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to input video, e.g. littering_sample.mp4")
    parser.add_argument("--out", default="boxes.csv", help="Output path (.csv or .json)")
    parser.add_argument("--weights", default="modelbest.pt", help="Model weights, e.g. modelbest.pt or yolov8n.pt")
    parser.add_argument("--tracker", default="bytetrack.yaml")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    extract(args.source, args.out, weights=args.weights, conf=args.conf, imgsz=args.imgsz, tracker=args.tracker)