from datetime import datetime, timezone
import math
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.errors import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.request import ServiceRequest
from app.models.service import Service
from app.models.user import User
from app.schemas import (
    AdminStatsResponse,
    CustomerHistorySummary,
    CustomerWithHistoryResponse,
    PaginatedCustomersResponse,
    PaginatedRequestsResponse,
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


# 3. Customer Requests & Order Flow Tracking (Search, Date Filter, Status Filter, Pagination)
@router.get("/requests", response_model=PaginatedRequestsResponse)
def get_all_requests(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query across customer name, email, phone, vehicle, ID"),
    status: Optional[str] = Query(None, description="Filter by status (Pending, Approved, In Progress, Completed, Rejected)"),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    time_slot: Optional[str] = Query(None, description="Filter by preferred time slot"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Retrieve service requests with search, date ranges, and server pagination."""
    query = (
        select(ServiceRequest)
        .join(ServiceRequest.customer)
        .outerjoin(ServiceRequest.service)
        .options(joinedload(ServiceRequest.customer), joinedload(ServiceRequest.service))
    )

    if status and status.strip():
        st_clean = status.strip()
        if st_clean.lower() == "active":
            query = query.where(ServiceRequest.status.in_(["Pending", "Approved", "In Progress"]))
        elif st_clean.lower() == "history":
            query = query.where(ServiceRequest.status.in_(["Completed", "Rejected"]))
        else:
            query = query.where(ServiceRequest.status == st_clean)

    if customer_id:
        query = query.where(ServiceRequest.customer_id == customer_id)

    if start_date and start_date.strip():
        query = query.where(ServiceRequest.preferred_date >= start_date.strip())

    if end_date and end_date.strip():
        query = query.where(ServiceRequest.preferred_date <= end_date.strip())

    if time_slot and time_slot.strip():
        query = query.where(ServiceRequest.preferred_time.ilike(f"%{time_slot.strip()}%"))

    if search and search.strip():
        term = f"%{search.strip()}%"
        # Check if search is numeric id
        id_cond = []
        if search.strip().replace("#", "").isdigit():
            id_cond.append(ServiceRequest.id == int(search.strip().replace("#", "")))

        query = query.where(
            or_(
                User.name.ilike(term),
                User.email.ilike(term),
                User.phone.ilike(term),
                ServiceRequest.vehicle_details.ilike(term),
                ServiceRequest.custom_service.ilike(term),
                Service.name.ilike(term),
                *id_cond,
            )
        )

    # Count total matching
    count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0

    # Paginate and order by newest first
    offset = (page - 1) * per_page
    paginated_stmt = query.order_by(ServiceRequest.created_at.desc()).offset(offset).limit(per_page)
    requests = db.scalars(paginated_stmt).all()

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
                admin_notes=r.admin_notes,
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

    total_pages = math.ceil(total / per_page) if total > 0 else 1
    return PaginatedRequestsResponse(
        items=results,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# 4. Privileged Customer Directory & Booking History
@router.get("/customers", response_model=PaginatedCustomersResponse)
def get_customers_with_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Admin privileged view: List customers with their booking summary and history."""
    query = select(User).where(User.role == "customer")

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                User.name.ilike(term),
                User.email.ilike(term),
                User.phone.ilike(term),
            )
        )

    total = db.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
    offset = (page - 1) * per_page
    users = db.scalars(query.order_by(User.created_at.desc()).offset(offset).limit(per_page)).all()

    items = []
    for u in users:
        # Fetch requests for this customer
        reqs = db.scalars(
            select(ServiceRequest)
            .options(joinedload(ServiceRequest.service))
            .where(ServiceRequest.customer_id == u.id)
            .order_by(ServiceRequest.created_at.desc())
        ).all()

        total_b = len(reqs)
        completed = sum(1 for r in reqs if r.status == "Completed")
        pending = sum(1 for r in reqs if r.status == "Pending")
        in_prog = sum(1 for r in reqs if r.status == "In Progress")
        approved = sum(1 for r in reqs if r.status == "Approved")
        rejected = sum(1 for r in reqs if r.status == "Rejected")

        recent = []
        for r in reqs[:5]:  # recent 5
            s_name = f"Custom: {r.custom_service}" if r.custom_service else (r.service.name if r.service else "Car Wash")
            recent.append(
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
                    customer_name=u.name,
                    customer_email=u.email,
                    customer_phone=u.phone,
                    service_name=s_name,
                    service_price=r.service.price if r.service else None,
                )
            )

        items.append(
            CustomerWithHistoryResponse(
                id=u.id,
                name=u.name,
                email=u.email,
                phone=u.phone,
                role=u.role,
                is_active=u.is_active,
                created_at=u.created_at,
                summary=CustomerHistorySummary(
                    total_bookings=total_b,
                    completed=completed,
                    pending=pending,
                    in_progress=in_prog,
                    approved=approved,
                    rejected=rejected,
                ),
                recent_requests=recent,
            )
        )

    total_pages = math.ceil(total / per_page) if total > 0 else 1
    return PaginatedCustomersResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# 5. Clean Dummy / Test Data Endpoint
@router.delete(
    "/cleanup-dummy-data",
    dependencies=[Depends(verify_csrf_token)],
)
def cleanup_dummy_data(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Permanently delete all mock/test customers and test requests, preserving admin and legitimate user."""
    # Delete requests associated with dummy customers or test data
    dummy_patterns = ["%example.com%", "%test%", "%dummy%"]
    dummy_users = db.scalars(
        select(User).where(
            or_(*[User.email.ilike(p) for p in dummy_patterns]),
            User.role != "admin",
        )
    ).all()

    dummy_user_ids = [u.id for u in dummy_users]
    deleted_requests_count = 0

    if dummy_user_ids:
        # SQLAlchemy cascade deletes requests when User is deleted
        for u in dummy_users:
            db.delete(u)

    # Also clean test requests that have mock descriptions like sfwfsf / sdfsfsf
    test_reqs = db.scalars(
        select(ServiceRequest).where(
            or_(
                ServiceRequest.vehicle_details.ilike("%sfwfsf%"),
                ServiceRequest.vehicle_details.ilike("%sdfsfsf%"),
                ServiceRequest.vehicle_details.ilike("%test%"),
            )
        )
    ).all()
    deleted_requests_count += len(test_reqs)
    for r in test_reqs:
        db.delete(r)

    db.commit()
    logger.info("Admin %s cleaned up %d dummy users and test requests", admin.email, len(dummy_users))

    return {
        "status": "success",
        "message": f"Successfully deleted {len(dummy_users)} dummy accounts and {deleted_requests_count} test requests.",
        "cleaned_users": len(dummy_users),
        "cleaned_requests": deleted_requests_count,
    }


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
    if data.admin_notes is not None:
        req.admin_notes = data.admin_notes.strip() if data.admin_notes else None
    if data.scheduled_date is not None and data.scheduled_date.strip():
        req.preferred_date = data.scheduled_date.strip()
    if data.scheduled_time is not None and data.scheduled_time.strip():
        req.preferred_time = data.scheduled_time.strip()

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
        admin_notes=req.admin_notes,
        status=req.status,
        created_at=req.created_at,
        decided_at=req.decided_at,
        customer_name=req.customer.name if req.customer else None,
        customer_email=req.customer.email if req.customer else None,
        customer_phone=req.customer.phone if req.customer else None,
        service_name=s_name,
        service_price=req.service.price if req.service else None,
    )
