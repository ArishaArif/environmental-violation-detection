from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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

class IncidentOut(IncidentBase):
    id: int
    timestamp: datetime
    review_status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True   # lets Pydantic read SQLAlchemy objects directly