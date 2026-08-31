# Environmental Violation Detection System

An AI-powered end-to-end platform designed to detect environmental violations (such as vehicle littering) from CCTV footage, extract license plate numbers using ANPR, and log incidents into a centralized management dashboard.

---

## 🏗 Project Architecture

```text
[ CCTV / Video Streams ]
          │
          ▼
   [ AI Pipeline ] ──────── (YOLO Detection & Tracking + ANPR)
          │
          ▼  (POST /incidents/)
 [ FastAPI Backend ] ────── (SQLAlchemy ORM) ────── [ PostgreSQL DB ]
          │
          ▼  (GET /incidents/)
[ Frontend Dashboard ]
```

### 📁 Directory Structure

```text
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── main.py          # Application entry point & CORS
│   │   ├── database.py      # Database engine & session setup
│   │   ├── models.py        # SQLAlchemy database schema
│   │   ├── schemas.py       # Pydantic data validation schemas
│   │   └── routers/
│   │       ├── incidents.py # Incident CRUD API endpoints
│   │       └── analytics.py # Analytics API endpoints
│   ├── .env                 # Local environment variables (ignored by Git)
│   └── requirements.txt     # Python dependencies
├── frontend/                 # React Dashboard (Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/      # TopBar, AppLayout
│   │   │   ├── incidents/   # IncidentCard, StatusButtonGroup, ViolationTag, PlateReadout
│   │   │   └── map/         # ViolationMap, MapLegend
│   │   ├── pages/           # FullConsole, IncidentDetail, ExpandedMap
│   │   ├── lib/             # incidents.js — shared formatting/labels
│   │   ├── mock/            # incidents.mock.json — local mock data
│   │   ├── theme/           # tokens.css — design tokens
│   │   ├── App.jsx          # Route definitions
│   │   └── main.jsx         # App entry point
│   ├── package.json
│   └── vite.config.js
├── ml-pipeline/              # ANPR Pipeline
│   ├── anpr_engine.py       # Core detection and plate extraction script
│   ├── test_pipeline.py     # Pipeline testing script
│   └── best.pt              # Trained ANPR YOLO model weights (Ignored by Git)
├── dl-pipeline/              # YOLO Detection & Littering Tracking Pipeline
│   ├── detect.py            # Vehicle tracking on sample input
│   ├── extract_boxes.py     # Per-frame vehicle box extraction to CSV
│   ├── detect_littering.py  # Motion-blob littering detection heuristic
│   ├── verify_candidates.py # Saves annotated frames for candidate review
│   ├── report_littering.py  # Ingestion bridge (ANPR + POST /incidents/)
│   ├── inspect_model.py     # Utility: prints a YOLO model's class list
│   └── modelbest.pt         # Vehicle-type YOLO model weights (Ignored by Git)
├── boxes.csv                 # Generated tracking data
├── candidates.csv            # Generated violation candidates
├── candidate_frames/         # Generated review frames
├── evidence/                 # Generated full-frame snapshot evidence
├── README.md
└── .gitignore
```

---

## 🚀 Local Setup & Installation

### Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** v18 or higher (for React Frontend)
- **Database:** PostgreSQL server running locally

---

### 1. Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:** Create a `.env` file inside the `backend/` directory with your local PostgreSQL connection parameters:
   ```env
   DATABASE_URL=postgresql://violation_user:yourpass@localhost:5432/violation_db
   ```

5. Start the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. **Interactive API Documentation:**
   - **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### 2. Frontend Setup (React + Vite)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node packages:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:5173](http://localhost:5173) in your web browser.

---

### 3. Machine Learning & Deep Learning Pipeline Setup

The AI pipeline is split across two directories using **two separate YOLO model weights**:

| Model Purpose | Directory | File Name | Source / Link |
| :--- | :--- | :--- | :--- |
| **ANPR Detector** | `ml-pipeline/` | `best.pt` | [Download from GitHub](https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8/raw/main/license_plate_detector.pt) |
| **Vehicle Detector** | `dl-pipeline/` | `modelbest.pt` | [Download from Google Drive](https://drive.google.com/drive/folders/1hE_iYE2TQKnzzMZWv9NJxmUBXncqiwLo?usp=sharing) |

1. Install dependencies for both pipelines:
   ```bash
   pip install ultralytics opencv-python numpy
   ```

2. Download and place the weights in their respective folders:
   - Save the license plate model as **`best.pt`** inside `ml-pipeline/`.
   - Save the custom vehicle model as **`modelbest.pt`** inside `dl-pipeline/`.

---

## 🚮 Littering Detection Execution

The tracking and detection scripts in `dl-pipeline/` feed processed violation candidates directly to the ANPR engine in `ml-pipeline/`, which logs verified incidents to the backend database.

Ensure your FastAPI backend is running before executing step 5. Navigate to the `dl-pipeline/` directory before running these commands:

```bash
cd dl-pipeline

# 1. Sanity check: Vehicle tracking visualization
python detect.py

# 2. Extract vehicle bounding boxes to CSV
python extract_boxes.py --source sample.mp4 --out ../boxes.csv --weights modelbest.pt

# 3. Run the littering detection heuristic
python detect_littering.py --source sample.mp4 --boxes ../boxes.csv

# 4. Generate annotated review frames
python verify_candidates.py --source sample.mp4

# 5. Process candidate ANPR and submit incident payload to backend API
python report_littering.py --source sample.mp4
```

---

## ⚠️ Known Limitations

- **Rule-Based Heuristic:** Littering detection uses motion-blob background subtraction (`MOG2`) rather than a trained 3D action recognition network.
- **Static Camera Assumption:** Requires fixed CCTV positions. Camera movement, pan, or tilt invalidates background subtraction assumptions.
- **Background Model Warm-up:** `BG_HISTORY` and `WARMUP_FRAMES` parameters must be adjusted according to input clip duration.
- **Derived Confidence Metric:** Confidence scores reflect track lifetime heuristics rather than calibrated probabilistic outputs.
- **Static Geolocation:** Incident locations default to preset baseline coordinates until per-camera GPS metadata integration is configured.

---

## 🎯 Stretch Goals & Future Work

- [ ] Train a 3D spatio-temporal action recognition model (e.g., MoViNet or SlowFast) for littering gesture classification.
- [ ] Implement optical flow frame registration to support dynamic/panning cameras.
- [ ] Integrate automated GIS mapping with real-time RTSP stream parsing per camera feed.
