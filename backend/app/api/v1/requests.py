from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.errors import NotFoundError, raise_error
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.request import ServiceRequest
from app.models.service import Service
from app.models.user import User
from app.schemas import ServiceRequestCreate, ServiceRequestResponse
from app.security import get_current_user, verify_csrf_token
from app.services.email import send_service_request_email

logger = get_logger("app.api.requests")
router = APIRouter(prefix="/requests", tags=["Service Requests"])


@router.post(
    "",
    response_model=ServiceRequestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf_token)],
)
def create_service_request(
    data: ServiceRequestCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Customer submits a new service request (standard package or custom request)."""
    service_name = "Custom Service"
    service_price = None

    if data.service_id:
        service = db.scalars(select(Service).where(Service.id == data.service_id)).first()
        if not service:
            raise NotFoundError(message="Selected service package does not exist")
        service_name = service.name
        service_price = service.price
    elif data.custom_service:
        service_name = f"Custom: {data.custom_service.strip()}"
    else:
        raise_error("Please select a service package or specify your custom service request", status_code=400)

    req = ServiceRequest(
        customer_id=current_user.id,
        service_id=data.service_id if data.service_id else None,
        custom_service=data.custom_service.strip() if data.custom_service else None,
        vehicle_details=data.vehicle_details.strip(),
        preferred_date=data.preferred_date.strip(),
        preferred_time=data.preferred_time.strip(),
        message=data.message.strip() if data.message else None,
        status="Pending",
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    logger.info("Service request created: id=%d by user=%d (%s) - %s", req.id, current_user.id, current_user.email, service_name)

    # Automatic email notification triggered in background
    background_tasks.add_task(
        send_service_request_email,
        customer_name=current_user.name,
        customer_email=current_user.email,
        service_name=service_name,
        vehicle_details=req.vehicle_details,
        date_str=req.preferred_date,
        time_str=req.preferred_time,
    )

    return ServiceRequestResponse(
        id=req.id,
        customer_id=req.customer_id,
        service_id=req.service_id,
        custom_service=req.custom_service,
        vehicle_details=req.vehicle_details,
        preferred_date=req.preferred_date,
        preferred_time=req.preferred_time,
        message=req.message,
        status=req.status,
        created_at=req.created_at,
        decided_at=req.decided_at,
        customer_name=current_user.name,
        customer_email=current_user.email,
        customer_phone=current_user.phone,
        service_name=service_name,
        service_price=service_price,
    )


@router.get("/my", response_model=List[ServiceRequestResponse])
def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all requests created by the authenticated customer."""
    stmt = (
        select(ServiceRequest)
        .options(joinedload(ServiceRequest.service))
        .where(ServiceRequest.customer_id == current_user.id)
        .order_by(ServiceRequest.created_at.desc())
    )
    requests = db.scalars(stmt).all()

    results = []
    for r in requests:
        s_name = f"Custom: {r.custom_service}" if r.custom_service else (r.service.name if r.service else "Car Wash Service")
        s_price = r.service.price if r.service else None
        results.append(
            ServiceRequestResponse(
                id=r.id,
                customer_id=r.customer_id,
                service_id=r.service_id,
                custom_service=r.custom_service,
                vehicle_details=r.vehicle_details,
                preferred_date=r.preferred_date,
                preferred_time=r.preferred_time,
                message=r.message,
                status=r.status,
                created_at=r.created_at,
                decided_at=r.decided_at,
                customer_name=current_user.name,
                customer_email=current_user.email,
                customer_phone=current_user.phone,
                service_name=s_name,
                service_price=s_price,
            )
        )
    return results
