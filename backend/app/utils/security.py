"""
Security utilities for device fingerprinting and hashing.
"""

import hashlib
from fastapi import Request


def generate_device_hash(request: Request, form_id: str) -> str:
    """
    Generate a unique device hash for one-response-per-device enforcement.
    
    Combines:
    - User-Agent header
    - Client IP address
    - Form ID
    
    Returns SHA-256 hash.
    """
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host if request.client else "unknown"
    
    # Combine components
    fingerprint = f"{user_agent}|{client_ip}|{form_id}"
    
    # Generate SHA-256 hash
    return hashlib.sha256(fingerprint.encode()).hexdigest()


def verify_jwt_token(token: str) -> dict:
    """
    Verify Supabase JWT token.
    Returns decoded token payload.
    """
    from jose import jwt, JWTError
    from app.config import get_settings
    
    settings = get_settings()
    
    try:
        # Supabase uses HS256 algorithm with the JWT secret
        # The secret is derived from the anon key
        payload = jwt.decode(
            token,
            settings.supabase_anon_key,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")
