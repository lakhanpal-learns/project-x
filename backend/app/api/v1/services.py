from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.service import Service
from app.schemas import ServiceResponse

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=List[ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    """Retrieve all available car wash and detailing services."""
    # These four names were placeholder demo packages from the original seed.
    # Keep their database rows intact for any historical requests, but do not
    # offer them to customers now that the official MrShine price list is seeded.
    legacy_demo_names = {
        "Exterior Car Wash",
        "Interior Cleaning",
        "Complete Cleaning",
        "Premium Detailing",
    }
    services = db.scalars(select(Service).order_by(Service.price.asc())).all()
    return [service for service in services if service.name not in legacy_demo_names]
