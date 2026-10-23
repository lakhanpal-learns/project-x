from typing import Optional
from fastapi import Depends, Header, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, UnauthorizedError
from app.db.session import get_db
from app.models.user import User
from app.security.csrf import verify_csrf_token
from app.security.tokens import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependency Injection: Retrieve the authenticated user from the JWT token."""
    if not token:
        raise UnauthorizedError(message="Authentication token missing")

    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError(message="Invalid token payload")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise UnauthorizedError(message="Invalid token subject")

    stmt = select(User).where(User.id == user_id)
    user = db.scalars(stmt).first()
    if not user:
        raise UnauthorizedError(message="User account no longer exists")

    if not user.is_active:
        raise ForbiddenError(message="Account has been deactivated")

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency Injection: Require that the authenticated user is an administrator."""
    if current_user.role != "admin":
        raise ForbiddenError(message="Administrator privileges required")
    return current_user


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Dependency Injection: Optional user extraction for public/semi-public routes."""
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub", 0))
        return db.scalars(select(User).where(User.id == user_id)).first()
    except Exception:
        return None
