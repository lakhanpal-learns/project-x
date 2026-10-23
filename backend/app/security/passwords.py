from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

_pwd_hash = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return _pwd_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2 hash."""
    if not hashed_password:
        return False
    try:
        return _pwd_hash.verify(plain_password, hashed_password)
    except Exception:
        return False
