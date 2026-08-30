# Environmental Violation Detection System

An AI-powered system designed to detect environmental violations (such as vehicle littering) from CCTV footage, extract license plate numbers using ANPR, and log incidents into a central management dashboard.

---

## 🏗 Project Architecture

```text
[ CCTV / Video Streams ]
          │
          ▼
   [ AI Pipeline ] ── (YOLO Detection & Tracking + ANPR)
          │
          ▼  (POST /incidents/)
    [ FastAPI Backend ] ── (SQLAlchemy ORM) ── [ PostgreSQL DB ]
          │
          ▼  (GET /incidents/)
  [ Frontend Dashboard ]
```

```text
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── main.py          # Application entry point & CORS
│   │   ├── database.py      # Database engine & session setup
│   │   ├── models.py        # SQLAlchemy database schema
│   │   ├── schemas.py       # Pydantic data validation schemas
│   │   └── routers/
│   │       └── incidents.py # Incident CRUD API endpoints
│   ├── .env                 # Local environment variables (ignored by git)
│   └── requirements.txt     # Python dependencies
├── frontend/                 # React Dashboard (Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/       # TopBar, AppLayout
│   │   │   ├── incidents/    # IncidentCard, StatusButtonGroup, ViolationTag, PlateReadout
│   │   │   └── map/          # ViolationMap, MapLegend
│   │   ├── pages/            # FullConsole, IncidentDetail, ExpandedMap
│   │   ├── lib/               # incidents.js — shared formatting/labels
│   │   ├── mock/              # incidents.mock.json — local mock data
│   │   ├── theme/             # tokens.css — design tokens
│   │   ├── App.jsx           # Route definitions
│   │   └── main.jsx          # App entry point
│   ├── package.json
│   └── vite.config.js
├── ml-pipeline/              # YOLO Detection & ANPR Pipeline
│   ├── anpr_engine.py       # Core detection and plate extraction script
│   ├── test_pipeline.py     # Pipeline testing script
│   └── best.pt              # Trained YOLO model weights (Ignored by Git, see setup)
├── README.md
└── .gitignore
```

## 📊 Dataset

The dataset used for the ANPR pipeline can be downloaded from [Google Drive](https://drive.google.com/drive/folders/15qSww4dpWfHkXgoQUGw79VJf8V02_td0?usp=sharing).

## Local Setup & Installation

### Prerequisites

- Python 3.10+
- PostgreSQL server running locally

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (Windows):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:** Create a `.env` file inside the `backend/` directory with your PostgreSQL connection string:
   ```
   DATABASE_URL=postgresql://violation_user:ouurpass@localhost:5432/violation_db
   ```
5. Start the API server:
   ```bash
   uvicorn app.main:app --reload
   ```
6. **Interactive API Documentation:** Once running, access the interactive Swagger docs at:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```

### ML Pipeline Setup

1. Navigate to the ml-pipeline directory:
   ```bash
   cd ml-pipeline
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Download the Model:** Download `license_plate_detector.pt` from the [Automatic-License-Plate-Recognition-using-YOLOv8](https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8) repo by Muhammad-Zeerak-Khan:
   ```
   https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8/raw/main/license_plate_detector.pt
   ```
   Rename it to `best.pt` and place it directly inside the `ml-pipeline/` directory.

   > Note: this is a general-purpose plate detector trained on Roboflow's public `license-plate-recognition-rxg4e` dataset — not Pakistan-specific.

4. Run the testing script:
   ```bash
   python test_pipeline.py
   ```
5. Run the ANPR engine:
   ```bash
   python anpr_engine.py
   ```
## 🚮 Littering Detection Pipeline

This extends `ml-pipeline/` with the upstream vehicle-tracking + littering-
detection stage that feeds into the existing ANPR engine and backend. It
produces the candidate incidents that `anpr_engine.py` reads plates from and
`report_littering.py` POSTs to `/incidents/`.

```text
[ CCTV / Video Streams ]
          │
          ▼
 [ Vehicle Tracking ] ── extract_boxes.py (YOLO + ByteTrack) ──► boxes.csv
          │
          ▼
 [ Littering Heuristic ] ── detect_littering.py (motion-blob separation) ──► candidates.csv
          │
          ▼
 [ Verification ] ── verify_candidates.py ──► candidate_frames/*.jpg
          │
          ▼
 [ Reporting ] ── report_littering.py ── ANPR (anpr_engine.py) ── POST /incidents/ ──► FastAPI Backend
```

### 📁 Structure

```text
├── ml-pipeline/
│   ├── anpr_engine.py             # (existing) plate extraction
│   ├── test_pipeline.py           # (existing) pipeline testing script
│   ├── license_plate_detector.pt  # (existing) ANPR model — see main setup above
│   ├── detect.py                  # Sanity check: vehicle tracking on sample.mp4
│   ├── extract_boxes.py           # Extracts per-frame vehicle boxes to boxes.csv
│   ├── detect_littering.py        # Littering heuristic, writes candidates.csv
│   ├── verify_candidates.py       # Saves annotated frames for candidate review
│   ├── inspect_model.py           # Utility: prints a YOLO model's class list
│   ├── report_littering.py        # candidates.csv + boxes.csv → ANPR → POST /incidents/
│   └── vehicle_model.pt           # Vehicle-type YOLO model — see Dataset below
│                                   # ⚠️ NOT the same file as license_plate_detector.pt —
│                                   #    keep filenames distinct, do not both save as best.pt
├── boxes.csv                      # generated
├── candidates.csv                 # generated
├── candidate_frames/              # generated
└── evidence/                      # generated — full-frame snapshots for reported incidents
```

### 📊 Dataset / Model Weights

The custom vehicle-type model (Auto-Rickshaw, Bike, Bus, Car, HCV, LCV, Toto,
Smoke classes) can be downloaded from [Google Drive](https://drive.google.com/drive/folders/1hE_iYE2TQKnzzMZWv9NJxmUBXncqiwLo?usp=sharing).

> ⚠️ Save this as `vehicle_model.pt` (or similarly distinct name) inside
> `ml-pipeline/` — **do not name it `best.pt`**, since that filename is
> already used by the ANPR license plate detector in this repo.

To verify a model's class list before using it:
```bash
python inspect_model.py --weights vehicle_model.pt
```

### 🛠 Setup

1. From `ml-pipeline/`, install the additional dependencies (on top of the
   existing `requirements.txt`):
   ```bash
   pip install ultralytics opencv-python numpy
   ```
2. Place your footage as `sample.mp4` (Step 4 sanity check) and/or
   `littering_sample.mp4` (full pipeline) inside `ml-pipeline/`.
3. Ensure the backend is running (`uvicorn app.main:app --reload` from
   `backend/`, per the main setup above) before running `report_littering.py`.

### ▶ Usage

```bash
# 1. Sanity check — vehicle tracking only, saves an annotated video
python detect.py

# 2. Extract vehicle boxes to CSV
python extract_boxes.py --source littering_sample.mp4 --out boxes.csv --weights vehicle_model.pt

# 3. Run the littering heuristic
python detect_littering.py --source littering_sample.mp4 --boxes boxes.csv

# 4. Visually verify candidates (saves annotated frames to candidate_frames/)
python verify_candidates.py --source littering_sample.mp4

# 5. Turn verified candidates into real incidents via ANPR + backend
python report_littering.py --source littering_sample.mp4
```

### ⚠️ Known Limitations

- **Heuristic, not a trained classifier.** Littering detection is rule-based
  (motion-blob separation + settling), not a trained action-recognition
  model. No COCO/vehicle-model class exists for "litter," so the thrown
  object is detected via background-subtraction motion, not classification.
- **Static camera assumption.** Motion-blob detection (`MOG2`) requires a
  fixed camera — panning/tracking/handheld footage gives unreliable results.
- **Short-clip background warm-up.** `BG_HISTORY` / `WARMUP_FRAMES` in
  `detect_littering.py` must be tuned relative to clip length, or the
  background model won't converge before the clip ends.
- **Confidence is a proxy, not calibrated ML output.** `report_littering.py`
  derives confidence from candidate track lifetime, capped at 0.9 — it is
  explicitly not a trained model's confidence score.
- **Placeholder GPS.** `DEFAULT_LOCATION` in `report_littering.py` is a
  placeholder Lahore coordinate pending real per-camera location data.

### 🎯 Stretch Goals

- Replace the motion-blob heuristic with a trained action-recognition model
  (e.g. MoViNet) once labeled littering clips are available.
- Camera-motion compensation so non-static footage can be used.
- Real GPS/location tagging per camera/deployment site.

5. Run the ANPR engine:
   ```bash
   python anpr_engine.py
   ```
