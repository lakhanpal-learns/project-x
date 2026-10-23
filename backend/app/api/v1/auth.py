from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ConflictError, UnauthorizedError, raise_error
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.user import User
from app.schemas import (
    CSRFTokenResponse,
    TokenResponse,
    UserLoginRequest,
    UserProfileUpdate,
    UserRegisterRequest,
    UserResponse,
)
from app.security import (
    create_access_token,
    generate_csrf_token,
    get_current_user,
    hash_password,
    verify_csrf_token,
    verify_password,
    CSRF_COOKIE_NAME,
)

logger = get_logger("app.api.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/csrf-token", response_model=CSRFTokenResponse)
def get_csrf_token(response: Response):
    """Generate a new signed CSRF token and set secure cookie."""
    token = generate_csrf_token()
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,
        samesite="lax",
        secure=settings.is_production,
    )
    return {"csrf_token": token}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf_token)],
)
def register(
    data: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new customer account."""
    clean_email = data.email.strip().lower()

    # Check if email is already registered
    existing_user = db.scalars(select(User).where(User.email == clean_email)).first()
    if existing_user:
        logger.warning("Registration attempt with existing email: %s", clean_email)
        raise ConflictError(message="An account with this email address already exists")

    # Check password strength
    if len(data.password) < settings.MIN_PASSWORD_LENGTH:
        raise_error(f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long", status_code=400)

    hashed = hash_password(data.password)
    new_user = User(
        name=data.full_name.strip(),
        email=clean_email,
        phone=data.phone.strip() if data.phone else None,
        password_hash=hashed,
        role="customer",
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("New user registered successfully: id=%d email=%s", new_user.id, new_user.email)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate customer or administrator and return JWT token."""
    clean_email = data.email.strip().lower()
    user = db.scalars(select(User).where(User.email == clean_email)).first()

    if not user or not verify_password(data.password, user.password_hash):
        logger.warning("Failed login attempt for email: %s", clean_email)
        raise UnauthorizedError(message="Invalid email address or password")

    if not user.is_active:
        raise UnauthorizedError(message="Your account is inactive. Please contact support.")

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "name": user.name,
    }
    access_token = create_access_token(token_payload)

    logger.info("User logged in: id=%d email=%s role=%s", user.id, user.email, user.role)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details of currently logged-in user."""
    return current_user


@router.put(
    "/profile",
    response_model=UserResponse,
    dependencies=[Depends(verify_csrf_token)],
)
def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile information (name, phone) for logged-in user."""
    if data.name:
        current_user.name = data.name.strip()
    if data.phone is not None:
        current_user.phone = data.phone.strip() if data.phone else None

    db.commit()
    db.refresh(current_user)
    logger.info("User %d (%s) updated profile", current_user.id, current_user.email)
    return current_user
