from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ServiceRequest(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True
    )
    custom_service: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    vehicle_details: Mapped[str] = mapped_column(String(255), nullable=False)
    preferred_date: Mapped[str] = mapped_column(String(50), nullable=False)
    preferred_time: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Pending", nullable=False)  # Pending, Approved, In Progress, Completed, Rejected
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    customer = relationship("User", back_populates="requests")
    service = relationship("Service", back_populates="requests")

    def __repr__(self) -> str:
        return f"<ServiceRequest id={self.id} customer_id={self.customer_id} status='{self.status}'>"
