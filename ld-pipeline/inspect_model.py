import argparse

from ultralytics import YOLO

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default="vehicle_detector.pt")
    args = parser.parse_args()

    model = YOLO(args.weights)

    print(f"Loaded: {args.weights}")
    print(f"Number of classes: {len(model.names)}")
    print("Class names:")
    for idx, name in model.names.items():
        print(f"  {idx}: {name}")

    # Quick sanity signal: does this look like stock COCO (80 classes,
    # starts with person/bicycle/car) or something custom?
    coco_first_five = ["person", "bicycle", "car", "motorcycle", "airplane"]
    actual_first_five = [model.names[i] for i in range(min(5, len(model.names)))]
    if actual_first_five == coco_first_five:
        print("\n=> Looks like standard COCO classes (unmodified or fine-tuned on same 80 classes).")
    else:
        print("\n=> Custom class set detected — NOT standard COCO. "
              "extract_boxes.py's class ID filters will need to be rewritten "
              "to match these class names/indices.")