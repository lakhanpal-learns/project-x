from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas import FeedbackCreate, FeedbackResponse
from app.security import get_optional_current_user, verify_csrf_token
from app.services.email import send_feedback_notification_email

logger = get_logger("app.api.feedback")
router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf_token)],
)
def submit_feedback(
    data: FeedbackCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Submit customer feedback/inquiry. Automatically triggers email notifications."""
    customer_id = current_user.id if current_user else None

    fb = Feedback(
        customer_id=customer_id,
        name=data.name.strip(),
        email=data.email.strip().lower(),
        phone=data.phone.strip() if data.phone else None,
        rating=data.rating,
        message=data.message.strip(),
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    logger.info("Feedback submitted: id=%d email=%s rating=%d", fb.id, fb.email, fb.rating)

    # Automatic background email notification
    background_tasks.add_task(
        send_feedback_notification_email,
        name=fb.name,
        email=fb.email,
        phone=fb.phone,
        rating=fb.rating,
        message=fb.message,
    )

    return fb
