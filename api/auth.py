"""
PulsePoint Cyber-Medical Intelligence System
API Authentication & RBAC FastAPI Dependencies
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status, Header
from core.security import verify_access_token, ROLE_PERMISSIONS, check_permission
from core.database import query_db

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Extracts Bearer token from Authorization header and returns user profile.
    Raises 401 Unauthorized if token is missing or invalid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization Header format. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or cryptographic signature invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    rows = query_db("SELECT id, username, full_name, email, role FROM users WHERE username = ?", (username,))
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user record no longer exists in system registry."
        )

    user = rows[0]
    return user


def require_roles(allowed_roles: List[str]):
    """Returns a dependency function that asserts current user possesses an allowed role."""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied. Role '{user_role}' lacks authorization for this resource."
            )
        return current_user
    return role_checker
