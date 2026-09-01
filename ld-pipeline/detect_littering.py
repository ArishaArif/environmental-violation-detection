import argparse
import csv
from collections import defaultdict
 
import cv2
import numpy as np
 
# ---- Tunable knobs ----
MIN_BLOB_AREA = 15          # px^2, ignore noise smaller than this
MAX_BLOB_AREA = 2500        # px^2, ignore blobs too big to be litter (whole cars etc.)
NEAR_VEHICLE_PX = 50        # blob must appear within this many px of a vehicle box
DIVERGE_MIN_PX = 25         # min CHANGE in blob-vs-vehicle offset (not raw distance!) to call it "separated"
DIVERGE_FRAMES = 8          # frames to check for divergence after first appearance
STATIONARY_WINDOW = 12      # frames to check for settling after divergence
STATIONARY_MAX_MOVE_PX = 10 # max blob movement allowed to call it "settled"
MIN_LIFETIME_FRAMES = 5     # blob track must persist at least this long (filters flicker/noise)
MIN_VEHICLE_MOVE_PX = 15    # vehicle must move at least this much during the window (filters parked cars)
BG_HISTORY = 50              # MOG2 background model history — should be well under your clip's frame count
WARMUP_FRAMES = 20           # frames used only to build the background model, not scanned for candidates
 
 
def load_vehicle_boxes(path):
    """frame -> list of vehicle rows from boxes.csv"""
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
 
 
def near_vehicle_edge(cx, cy, veh, thresh=NEAR_VEHICLE_PX):
    ex1, ey1, ex2, ey2 = veh["x1"] - thresh, veh["y1"] - thresh, veh["x2"] + thresh, veh["y2"] + thresh
    inside_padded = ex1 <= cx <= ex2 and ey1 <= cy <= ey2
    inside_core = veh["x1"] < cx < veh["x2"] and veh["y1"] < cy < veh["y2"]
    return inside_padded and not inside_core
 
 
def vehicle_center_at(vehicle_frames, frame_idx, track_id):
    for v in vehicle_frames.get(frame_idx, []):
        if v["track_id"] == track_id:
            return ((v["x1"] + v["x2"]) / 2, (v["y1"] + v["y2"]) / 2)
    return None
 
 
def find_motion_blobs(source, vehicle_frames):
    """
    Runs background-subtraction motion detection frame by frame.
    For each frame, finds small blobs near a vehicle edge and tracks them
    forward with simple nearest-neighbor matching (good enough for a short
    MVP clip — swap for a real tracker later if this gets noisy).
    """
    cap = cv2.VideoCapture(source)
    backsub = cv2.createBackgroundSubtractorMOG2(history=BG_HISTORY, varThreshold=25, detectShadows=False)
 
    blob_tracks = defaultdict(list)  # blob_id -> [(frame, cx, cy, nearby_vehicle_tid), ...]
    next_blob_id = 0
    active_blobs = {}  # blob_id -> (cx, cy) last seen, for nearest-neighbor continuation
 
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
 
        fg = backsub.apply(frame)
 
        if frame_idx < WARMUP_FRAMES:
            # Still building the background model — don't trust blobs yet,
            # but keep feeding frames so the model converges.
            frame_idx += 1
            continue
 
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 
        this_frame_blobs = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < MIN_BLOB_AREA or area > MAX_BLOB_AREA:
                continue
            x, y, w, h = cv2.boundingRect(c)
            cx, cy = x + w / 2, y + h / 2
            this_frame_blobs.append((cx, cy))
 
        # match to active tracks (nearest neighbor within a small radius), else start new track
        matched_ids = set()
        for (cx, cy) in this_frame_blobs:
            best_id, best_dist = None, 40  # px match radius
            for bid, (pcx, pcy) in active_blobs.items():
                if bid in matched_ids:
                    continue
                d = ((cx - pcx) ** 2 + (cy - pcy) ** 2) ** 0.5
                if d < best_dist:
                    best_id, best_dist = bid, d
            if best_id is None:
                best_id = next_blob_id
                next_blob_id += 1
 
            nearby_vehicle_tid = None
            for veh in vehicle_frames.get(frame_idx, []):
                if near_vehicle_edge(cx, cy, veh):
                    nearby_vehicle_tid = veh["track_id"]
                    break
 
            blob_tracks[best_id].append((frame_idx, cx, cy, nearby_vehicle_tid))
            active_blobs[best_id] = (cx, cy)
            matched_ids.add(best_id)
 
        # drop blobs not seen this frame (simple — no occlusion handling for MVP)
        active_blobs = {bid: pos for bid, pos in active_blobs.items()
                         if blob_tracks[bid][-1][0] == frame_idx}
 
        frame_idx += 1
 
    cap.release()
    return blob_tracks
 
 
def evaluate_candidates(blob_tracks, vehicle_frames):
    candidates = []
 
    for blob_id, track in blob_tracks.items():
        if len(track) < MIN_LIFETIME_FRAMES:
            continue
 
        first_frame, fcx, fcy, veh_tid = track[0]
        if veh_tid is None:
            continue  # didn't originate near any vehicle
 
        # Baseline: blob position relative to the vehicle at first sighting.
        # (Blobs near the box edge start with a nonzero offset from center —
        # that's expected and NOT divergence. We need the offset to CHANGE.)
        v0 = vehicle_center_at(vehicle_frames, first_frame, veh_tid)
        if v0 is None:
            continue
        offset0 = (fcx - v0[0], fcy - v0[1])
 
        diverged, diverge_at = False, None
        vehicle_positions = []
        for (f, cx, cy, _) in track[:DIVERGE_FRAMES]:
            vcenter = vehicle_center_at(vehicle_frames, f, veh_tid)
            if vcenter is None:
                continue
            vehicle_positions.append(vcenter)
            offset_t = (cx - vcenter[0], cy - vcenter[1])
            offset_change = ((offset_t[0] - offset0[0]) ** 2 + (offset_t[1] - offset0[1]) ** 2) ** 0.5
            if offset_change > DIVERGE_MIN_PX:
                diverged, diverge_at = True, f
                break
        if not diverged:
            continue
 
        # Require the vehicle to actually be moving in this window — a parked
        # car surrounded by background-subtraction noise (shadows, reflections)
        # shouldn't count as a littering event.
        if len(vehicle_positions) >= 2:
            vx0, vy0 = vehicle_positions[0]
            vx1, vy1 = vehicle_positions[-1]
            vehicle_move = ((vx1 - vx0) ** 2 + (vy1 - vy0) ** 2) ** 0.5
            if vehicle_move < MIN_VEHICLE_MOVE_PX:
                continue
 
        # check settling after divergence
        post = [p for p in track if p[0] >= diverge_at][:STATIONARY_WINDOW]
        if len(post) < 3:
            continue
        xs = [p[1] for p in post]
        ys = [p[2] for p in post]
        spread = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5
        if spread <= STATIONARY_MAX_MOVE_PX:
            candidates.append(
                {
                    "blob_id": blob_id,
                    "vehicle_track_id": veh_tid,
                    "first_seen_frame": first_frame,
                    "diverge_frame": diverge_at,
                    "settled_at": (round(xs[-1], 1), round(ys[-1], 1)),
                    "lifetime_frames": len(track),
                }
            )
 
    return candidates
 
 
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Original video, e.g. littering_sample.mp4")
    parser.add_argument("--boxes", default="boxes.csv", help="Vehicle box CSV from extract_boxes.py")
    parser.add_argument("--out", default="candidates.csv", help="Where to write candidate events as CSV")
    args = parser.parse_args()
 
    vehicle_frames = load_vehicle_boxes(args.boxes)
    print("Scanning for motion blobs (this re-reads the video, may take a moment)...")
    blob_tracks = find_motion_blobs(args.source, vehicle_frames)
    print(f"Tracked {len(blob_tracks)} raw motion blobs total.")
 
    candidates = evaluate_candidates(blob_tracks, vehicle_frames)
 
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "blob_id", "vehicle_track_id", "first_seen_frame",
                "diverge_frame", "settled_x", "settled_y", "lifetime_frames",
            ],
        )
        writer.writeheader()
        for c in candidates:
            writer.writerow(
                {
                    "blob_id": c["blob_id"],
                    "vehicle_track_id": c["vehicle_track_id"],
                    "first_seen_frame": c["first_seen_frame"],
                    "diverge_frame": c["diverge_frame"],
                    "settled_x": c["settled_at"][0],
                    "settled_y": c["settled_at"][1],
                    "lifetime_frames": c["lifetime_frames"],
                }
            )
    print(f"Wrote {len(candidates)} candidate(s) to {args.out}")
 
    if not candidates:
        print("No candidate littering events found. Try loosening NEAR_VEHICLE_PX, "
              "DIVERGE_MIN_PX, MIN_BLOB_AREA/MAX_BLOB_AREA, or MIN_LIFETIME_FRAMES.")
        return
 
    print(f"\nFound {len(candidates)} candidate littering event(s):\n")
    for c in candidates:
        print(
            f"  blob {c['blob_id']} — appeared near vehicle {c['vehicle_track_id']} "
            f"at frame {c['first_seen_frame']}, diverged at frame {c['diverge_frame']}, "
            f"settled near {c['settled_at']} (tracked {c['lifetime_frames']} frames)"
        )
 
 
if __name__ == "__main__":
    main()