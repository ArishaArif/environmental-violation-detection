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
├── README.md
└── .gitignore

Local Setup & Installation
Prerequisites
Python 3.10+
PostgreSQL server running locally
Backend Setup
Navigate to the backend directory:
cd backend
Create and activate a virtual environment:(windows)
python -m venv venv
venv\Scripts\activate
Install dependencies:
pip install -r requirements.txt
Environment Variables:
Create a .env file inside the backend/ directory with your PostgreSQL connection string:
DATABASE_URL=postgresql://violation_user:ouurpass@localhost:5432/violation_db
Start the API Server:
uvicorn app.main:app --reload
Interactive API Documentation:
Once running, access the interactive Swagger docs at:
Swagger UI: http://127.0.0.1:8000/docs
Health Check: http://127.0.0.1:8000/health

Frontend Setup
Navigate to the frontend directory:
   cd frontend
Install dependencies:
   npm install
Start the dev server:
   npm run dev
