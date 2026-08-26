from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/incidents", tags=["incidents"])

# CREATE
@router.post("/", response_model=schemas.IncidentOut, status_code=201)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    db_incident = models.Incident(**incident.model_dump())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

# LIST (with optional filters)
@router.get("/", response_model=List[schemas.IncidentOut])
def list_incidents(
    violation_type: Optional[str] = None,
    review_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(models.Incident)
    if violation_type:
        query = query.filter(models.Incident.violation_type == violation_type)
    if review_status:
        query = query.filter(models.Incident.review_status == review_status)
    return query.order_by(models.Incident.timestamp.desc()).offset(skip).limit(limit).all()

# GET ONE
@router.get("/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

# UPDATE (review status)
@router.patch("/{incident_id}", response_model=schemas.IncidentOut)
def update_incident(incident_id: int, update: schemas.IncidentUpdate, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(incident, key, value)
    db.commit()
    db.refresh(incident)
    return incident

# DELETE (useful for cleaning up test data)
@router.delete("/{incident_id}", status_code=204)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    db.delete(incident)
    db.commit()
    return None