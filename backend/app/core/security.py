"""
security.py
-----------
Defines security constants, configurations, and utility functions such as
password hashing and verification, primarily used during user authentication
and authorization processes.
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt

# Password hashing context (using bcrypt as the default standard)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration Constants
# Use the config settings to determine the secret key and algorithm
from ..core.config import get_settings

settings = get_settings()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Token expiration time


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a password using the configured scheme."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a JSON Web Token (JWT) for authentication.
    Firebase custom tokens handle the primary auth, this structure is essential for standard FastAPI usage.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "sub": "access_token"})
    encoded_jwt = jwt.encode(to_encode, settings.AUTH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt