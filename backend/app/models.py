from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    violation_type = Column(String, nullable=False)      # "littering" 
    confidence = Column(Float, nullable=False)            # 0.0–1.0 from the AI model
    plate_number = Column(String, nullable=True)          # from ANPR, may be null
    plate_confidence = Column(Float, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    evidence_path = Column(String, nullable=True)         # path/URL to the saved frame image
    review_status = Column(String, default="pending")     # pending | accepted | rejected | needs_investigation
    notes = Column(Text, nullable=True)