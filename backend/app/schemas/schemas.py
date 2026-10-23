from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Authentication Schemas
class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(None, max_length=30)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: str


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# CSRF Schema
class CSRFTokenResponse(BaseModel):
    csrf_token: str


# Service Schemas
class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    duration_minutes: int = Field(60, ge=5, le=720)
    image_url: Optional[str] = None


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, ge=5, le=720)
    image_url: Optional[str] = None


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    duration_minutes: int
    image_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# Service Request Schemas
class ServiceRequestCreate(BaseModel):
    service_id: Optional[int] = None
    custom_service: Optional[str] = Field(None, max_length=100)
    vehicle_details: str = Field(..., min_length=2, max_length=255)
    preferred_date: str = Field(..., min_length=4, max_length=50)
    preferred_time: str = Field(..., min_length=2, max_length=50)
    message: Optional[str] = None


# Extended Multi-stage Order Status for Tracking System
class ServiceRequestStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(Pending|Approved|In Progress|Completed|Rejected)$")
    admin_notes: Optional[str] = None


class ServiceRequestResponse(BaseModel):
    id: int
    customer_id: int
    service_id: Optional[int] = None
    custom_service: Optional[str] = None
    vehicle_details: str
    preferred_date: str
    preferred_time: str
    message: Optional[str]
    status: str
    created_at: datetime
    decided_at: Optional[datetime] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    service_name: Optional[str] = None
    service_price: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


# Feedback Schemas
class FeedbackCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    rating: int = Field(5, ge=1, le=5)
    message: str = Field(..., min_length=5)


class FeedbackResponse(BaseModel):
    id: int
    name: str
    email: str
    rating: int
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Admin Stats Schema
class AdminStatsResponse(BaseModel):
    total_requests: int
    pending_requests: int
    approved_requests: int
    in_progress_requests: int
    completed_requests: int
    rejected_requests: int
    total_customers: int
