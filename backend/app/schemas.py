from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import Optional

# Base URL where evidence files are served from (static mount in main.py)
EVIDENCE_BASE_URL = "http://127.0.0.1:8000/evidence"


class IncidentBase(BaseModel):
    violation_type: str
    confidence: float
    plate_number: Optional[str] = None
    plate_confidence: Optional[float] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    evidence_path: Optional[str] = None


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    review_status: Optional[str] = None
    notes: Optional[str] = None


class IncidentOut(BaseModel):
    id: int
    timestamp: datetime
    violation_type: str
    confidence: float
    plate_number: Optional[str] = None
    plate_confidence: Optional[float] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    evidence_path: Optional[str] = None
    review_status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

    @computed_field
    @property
    def evidence_url(self) -> Optional[str]:
        if self.evidence_path:
            return f"{EVIDENCE_BASE_URL}/{self.evidence_path}"
        return None