# Environmental Violation Detection System

An AI-powered system designed to detect environmental violations (such as vehicle littering and exhaust smoke) from CCTV footage, extract license plate numbers using ANPR, and log incidents into a central management dashboard.

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

5. Run the ANPR engine:
   ```bash
   python anpr_engine.py
   ```
