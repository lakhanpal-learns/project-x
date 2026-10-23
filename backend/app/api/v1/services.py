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
    services = db.scalars(select(Service).order_by(Service.price.asc())).all()
    return services
