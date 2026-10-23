from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.errors import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.request import ServiceRequest
from app.models.service import Service
from app.models.user import User
from app.schemas import (
    AdminStatsResponse,
    ServiceCreate,
    ServiceResponse,
    ServiceRequestResponse,
    ServiceRequestStatusUpdate,
    ServiceUpdate,
)
from app.security import get_current_admin, verify_csrf_token
from app.services.email import send_status_update_email

logger = get_logger("app.api.admin")
router = APIRouter(prefix="/admin", tags=["Admin Portal"])


# 1. Statistics
@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Retrieve aggregate statistics for the admin dashboard."""
    total_reqs = db.scalar(select(func.count(ServiceRequest.id))) or 0
    pending_reqs = (
        db.scalar(select(func.count(ServiceRequest.id)).where(ServiceRequest.status == "Pending")) or 0
    )
    approved_reqs = (
        db.scalar(select(func.count(ServiceRequest.id)).where(ServiceRequest.status == "Approved")) or 0
    )
    in_progress_reqs = (
        db.scalar(select(func.count(ServiceRequest.id)).where(ServiceRequest.status == "In Progress")) or 0
    )
    completed_reqs = (
        db.scalar(select(func.count(ServiceRequest.id)).where(ServiceRequest.status == "Completed")) or 0
    )
    rejected_reqs = (
        db.scalar(select(func.count(ServiceRequest.id)).where(ServiceRequest.status == "Rejected")) or 0
    )
    total_users = db.scalar(select(func.count(User.id)).where(User.role == "customer")) or 0

    return AdminStatsResponse(
        total_requests=total_reqs,
        pending_requests=pending_reqs,
        approved_requests=approved_reqs,
        in_progress_requests=in_progress_reqs,
        completed_requests=completed_reqs,
        rejected_requests=rejected_reqs,
        total_customers=total_users,
    )


# 2. Service Package Management (Add, Edit, Delete packages)
@router.post(
    "/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf_token)],
)
def create_service_package(
    data: ServiceCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Admin creates a new service package."""
    existing = db.scalars(select(Service).where(Service.name == data.name.strip())).first()
    if existing:
        raise ConflictError(message="A service package with this name already exists")

    new_svc = Service(
        name=data.name.strip(),
        description=data.description.strip() if data.description else None,
        price=data.price,
        duration_minutes=data.duration_minutes,
        image_url=data.image_url.strip() if data.image_url else "/assets/images/exterior-wash.jpg",
    )
    db.add(new_svc)
    db.commit()
    db.refresh(new_svc)

    logger.info("Admin %s created service package: %s ($%s)", admin.email, new_svc.name, new_svc.price)
    return new_svc


@router.put(
    "/services/{service_id}",
    response_model=ServiceResponse,
    dependencies=[Depends(verify_csrf_token)],
)
def update_service_package(
    service_id: int,
    data: ServiceUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Admin updates an existing service package."""
    svc = db.scalars(select(Service).where(Service.id == service_id)).first()
    if not svc:
        raise NotFoundError(message="Service package not found")

    if data.name is not None:
        svc.name = data.name.strip()
    if data.description is not None:
        svc.description = data.description.strip()
    if data.price is not None:
        svc.price = data.price
    if data.duration_minutes is not None:
        svc.duration_minutes = data.duration_minutes
    if data.image_url is not None:
        svc.image_url = data.image_url.strip()

    db.commit()
    db.refresh(svc)
    logger.info("Admin %s updated service package %d: %s", admin.email, svc.id, svc.name)
    return svc


@router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_csrf_token)],
)
def delete_service_package(
    service_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Admin deletes a service package."""
    svc = db.scalars(select(Service).where(Service.id == service_id)).first()
    if not svc:
        raise NotFoundError(message="Service package not found")

    svc_name = svc.name
    db.delete(svc)
    db.commit()
    logger.info("Admin %s deleted service package: %s (id: %d)", admin.email, svc_name, service_id)
    return {"status": "success", "message": f"Service package '{svc_name}' deleted"}


# 3. Customer Requests & Order Flow Tracking
@router.get("/requests", response_model=List[ServiceRequestResponse])
def get_all_requests(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Retrieve all service requests across all customers."""
    stmt = (
        select(ServiceRequest)
        .options(joinedload(ServiceRequest.customer), joinedload(ServiceRequest.service))
        .order_by(ServiceRequest.created_at.desc())
    )
    requests = db.scalars(stmt).all()

    results = []
    for r in requests:
        s_name = (
            f"✨ Custom: {r.custom_service}"
            if r.custom_service
            else (r.service.name if r.service else "Car Wash Service")
        )
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
                customer_name=r.customer.name if r.customer else "Unknown",
                customer_email=r.customer.email if r.customer else "Unknown",
                customer_phone=r.customer.phone if r.customer else None,
                service_name=s_name,
                service_price=s_price,
            )
        )
    return results


@router.patch(
    "/requests/{request_id}/status",
    response_model=ServiceRequestResponse,
    dependencies=[Depends(verify_csrf_token)],
)
def update_request_status(
    request_id: int,
    data: ServiceRequestStatusUpdate,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Approve, start, complete, or reject a service request and trigger email notification."""
    stmt = (
        select(ServiceRequest)
        .options(joinedload(ServiceRequest.customer), joinedload(ServiceRequest.service))
        .where(ServiceRequest.id == request_id)
    )
    req = db.scalars(stmt).first()
    if not req:
        raise NotFoundError(message="Service request not found")

    old_status = req.status
    req.status = data.status
    req.decided_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)

    logger.info("Admin %s updated request %d: %s -> %s", admin.email, req.id, old_status, req.status)

    s_name = (
        f"Custom Request: {req.custom_service}"
        if req.custom_service
        else (req.service.name if req.service else "Car Wash Service")
    )

    # Automatic background email notification
    if req.customer and req.customer.email:
        background_tasks.add_task(
            send_status_update_email,
            customer_name=req.customer.name,
            customer_email=req.customer.email,
            service_name=s_name,
            status=req.status,
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
        customer_name=req.customer.name if req.customer else None,
        customer_email=req.customer.email if req.customer else None,
        customer_phone=req.customer.phone if req.customer else None,
        service_name=s_name,
        service_price=req.service.price if req.service else None,
    )
