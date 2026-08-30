import argparse
import csv
import os

import cv2


def load_candidates(path):
    candidates = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            candidates.append(
                {
                    "first_seen_frame": int(row["first_seen_frame"]),
                    "diverge_frame": int(row["diverge_frame"]),
                    "x": float(row["settled_x"]),
                    "y": float(row["settled_y"]),
                    "veh_id": row["vehicle_track_id"],
                }
            )
    return candidates


def dump_frames(source, candidates, out_dir="candidate_frames"):
    os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(source)

    # Group by diverge_frame so we only decode the video once.
    targets = {}
    for c in candidates:
        targets.setdefault(c["diverge_frame"], []).append(c)

    if not targets:
        print("No candidates to verify — candidates.csv was empty.")
        return

    frame_idx = 0
    saved = 0
    max_target = max(targets)
    while frame_idx <= max_target:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx in targets:
            for c in targets[frame_idx]:
                annotated = frame.copy()
                cx, cy = int(c["x"]), int(c["y"])
                cv2.circle(annotated, (cx, cy), 15, (0, 0, 255), 3)
                cv2.putText(
                    annotated,
                    f"first_seen={c['first_seen_frame']} diverge={frame_idx} veh={c['veh_id']}",
                    (max(cx - 200, 10), max(cy - 25, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2,
                )
                out_path = os.path.join(
                    out_dir,
                    f"f{c['first_seen_frame']:04d}_diverge{frame_idx:04d}_veh{c['veh_id']}.jpg",
                )
                cv2.imwrite(out_path, annotated)
                saved += 1
        frame_idx += 1

    cap.release()
    print(f"Saved {saved} annotated frame(s) to ./{out_dir}/")
    print("Open that folder and flip through the images — red circle marks the "
          "flagged object location. Real littering events should show something "
          "visibly airborne/landed there; noise will show nothing unusual.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--candidates", default="candidates.csv")
    parser.add_argument("--out_dir", default="candidate_frames")
    args = parser.parse_args()

    candidates = load_candidates(args.candidates)
    dump_frames(args.source, candidates, args.out_dir)