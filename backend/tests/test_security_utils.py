import pytest

from app.core.errors import UnauthorizedError
from app.security.csrf import generate_csrf_token, validate_csrf_token
from app.security.passwords import hash_password, verify_password
from app.security.tokens import create_access_token, decode_access_token


def test_csrf_token_round_trip_and_tampering():
    token = generate_csrf_token()
    assert validate_csrf_token(token)

    parts = token.split(":")
    parts[1] = "0" * len(parts[1])
    assert not validate_csrf_token(":".join(parts))


def test_csrf_rejects_missing_and_malformed_tokens():
    assert not validate_csrf_token(None)
    assert not validate_csrf_token("")
    assert not validate_csrf_token("not-a-valid-token")


def test_password_hash_verifies_only_matching_password():
    encoded = hash_password("correct horse battery staple")
    assert encoded != "correct horse battery staple"
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("wrong password", encoded)


def test_jwt_round_trip_and_rejects_invalid_token():
    token = create_access_token({"sub": "123", "role": "customer"})
    payload = decode_access_token(token)
    assert payload["sub"] == "123"
    assert payload["role"] == "customer"

    with pytest.raises(UnauthorizedError):
        decode_access_token("not-a-jwt")
