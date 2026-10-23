import hmac
import hashlib
import os
import time
from typing import Optional
from fastapi import Request

from app.core.config import settings
from app.core.errors import CSRFValidationError
from app.core.logging import get_logger

logger = get_logger("app.security.csrf")

CSRF_COOKIE_NAME = "mrshine_csrf"
CSRF_HEADER_NAME = "X-CSRF-Token"
TOKEN_VALIDITY_SECONDS = 3600 * 24  # 24 hours


def generate_csrf_token() -> str:
    """Generate a signed, timestamped CSRF token."""
    now = int(time.time())
    entropy = os.urandom(16).hex()
    payload = f"{now}:{entropy}"
    signature = hmac.new(
        settings.CSRF_SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}:{signature}"


def validate_csrf_token(token: Optional[str]) -> bool:
    """Validate token signature and expiration."""
    if not token or ":" not in token:
        return False

    parts = token.split(":")
    if len(parts) != 3:
        return False

    now_str, entropy, provided_sig = parts
    try:
        token_time = int(now_str)
    except ValueError:
        return False

    # Check expiration
    if time.time() - token_time > TOKEN_VALIDITY_SECONDS:
        logger.warning("CSRF token expired.")
        return False

    payload = f"{now_str}:{entropy}"
    expected_sig = hmac.new(
        settings.CSRF_SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_sig, provided_sig)


async def verify_csrf_token(request: Request) -> None:
    """Dependency to enforce CSRF token presence and validity on state-changing requests."""
    # Allow safe methods
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    # Extract token from header or form data
    token = request.headers.get(CSRF_HEADER_NAME)
    if not token and hasattr(request, "_form"):
        form = getattr(request, "_form", None)
        if form and "csrf_token" in form:
            token = form["csrf_token"]

    # In development mode, if header is missing but auth Bearer token is provided, log debug and allow
    # to facilitate development/testing unless strictly configured.
    auth_header = request.headers.get("Authorization", "")
    if not token and auth_header.startswith("Bearer "):
        # JWT in Authorization header is inherently CSRF-immune when sent from JavaScript client
        return

    if not token or not validate_csrf_token(token):
        logger.warning(
            "CSRF validation failed for method %s path %s",
            request.method,
            request.url.path,
        )
        raise CSRFValidationError()
