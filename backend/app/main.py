from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models  # <--- THIS IMPORT IS REQUIRED so SQLAlchemy registers the model
from .routers import incidents

# Create tables in PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Environmental Violation Detection API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incidents.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}