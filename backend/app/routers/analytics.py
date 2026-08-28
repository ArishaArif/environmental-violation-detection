from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Numeric
from .. import models
from ..database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/")
def get_analytics(db: Session = Depends(get_db)):
    by_type_rows = (
        db.query(models.Incident.violation_type, func.count(models.Incident.id))
        .group_by(models.Incident.violation_type)
        .all()
    )
    by_type = {vtype: count for vtype, count in by_type_rows}

    by_day_rows = (
        db.query(
            func.date(models.Incident.timestamp).label("day"),
            func.count(models.Incident.id),
        )
        .group_by(func.date(models.Incident.timestamp))
        .order_by(func.date(models.Incident.timestamp))
        .all()
    )
    by_day = [{"date": str(day), "count": count} for day, count in by_day_rows]

    by_hotspot_rows = (
        db.query(
            func.round(cast(models.Incident.location_lat, Numeric), 2).label("lat"),
            func.round(cast(models.Incident.location_lng, Numeric), 2).label("lng"),
            func.count(models.Incident.id),
        )
        .filter(models.Incident.location_lat.isnot(None))
        .group_by("lat", "lng")
        .all()
    )
    by_hotspot = [
        {"lat": float(lat), "lng": float(lng), "count": count}
        for lat, lng, count in by_hotspot_rows
    ]

    total_incidents = db.query(models.Incident).count()
    pending_review = (
        db.query(models.Incident)
        .filter(models.Incident.review_status == "pending")
        .count()
    )

    return {
        "total_incidents": total_incidents,
        "pending_review": pending_review,
        "by_type": by_type,
        "by_day": by_day,
        "by_hotspot": by_hotspot,
    }