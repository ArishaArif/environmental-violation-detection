from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine, Base
from . import models  # Ensures SQLAlchemy registers models
from .routers import incidents, analytics

# 1. Create database tables
Base.metadata.create_all(bind=engine)

# 2. Initialize FastAPI app (ONCE)
app = FastAPI(title="Environmental Violation Detection API")

# 3. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Mount Static Files for Evidence
app.mount("/evidence", StaticFiles(directory="evidence"), name="evidence")

# 5. Include Routers
app.include_router(incidents.router)
app.include_router(analytics.router)

# 6. Health Check Endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}