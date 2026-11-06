"""Authentication and User Session API Endpoints.

Architectural and Security Rationale:
- Provides system login and session verification for Administrators and Civil Status Officers.
- Credentials:
  * Administrator: admin / admin123
  * Civil Status Officer: user / user123
- Adheres to snake_case naming conventions and Zero Data Retention (ZDR) policy.
"""

import logging
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import LoginRequest, LoginResponse, UserProfile

logger = logging.getLogger("auth_endpoint")

auth_router = APIRouter(
    prefix="/auth",
    tags=["system_authentication"],
)

# Canonical system credential mappings
USERS_DATABASE: Dict[str, Dict[str, Any]] = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "full_name_km": "អភិបាលប្រព័ន្ធរដ្ឋបាល",
        "full_name_en": "System Administrator",
        "department_km": "ការិយាល័យអត្រានុកូលដ្ឋាន និងអត្តសញ្ញាណប័ណ្ណ",
        "department_en": "Civil Registration and Identification Bureau",
        "permissions": ["manage_divisions", "review_reports", "edit_templates", "delete_records"],
    },
    "user": {
        "password": "user123",
        "role": "user",
        "full_name_km": "មន្ត្រីចុះបញ្ជីអត្រានុកូលដ្ឋាន",
        "full_name_en": "Civil Status Registrar",
        "department_km": "ផ្នែកទទួលពាក្យ និងផ្ទៀងផ្ទាត់ទិន្នន័យ",
        "department_en": "Application Intake and Verification Section",
        "permissions": ["report_issues", "view_divisions", "verify_documents"],
    },
}


@auth_router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate User or System Administrator",
    description="Validates administrative credentials and returns an access token with role permissions.",
)
async def login(payload: LoginRequest) -> LoginResponse:
    """Authenticates system credentials."""
    username = payload.username.strip().lower()
    password = payload.password.strip()

    user_record = USERS_DATABASE.get(username)
    if not user_record or user_record["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ឈ្មោះអ្នកប្រើប្រាស់ ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវ (Invalid username or password).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    profile = UserProfile(
        username=username,
        role=user_record["role"],
        full_name_km=user_record["full_name_km"],
        full_name_en=user_record["full_name_en"],
        department_km=user_record["department_km"],
        department_en=user_record["department_en"],
        permissions=user_record["permissions"],
    )

    token = f"token_ocrbc_{username}_{user_record['role']}"

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=profile,
    )


@auth_router.get(
    "/me",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
)
async def get_current_user_profile(username: str = "admin") -> UserProfile:
    """Retrieves current user details."""
    user_record = USERS_DATABASE.get(username, USERS_DATABASE["admin"])
    return UserProfile(
        username=username,
        role=user_record["role"],
        full_name_km=user_record["full_name_km"],
        full_name_en=user_record["full_name_en"],
        department_km=user_record["department_km"],
        department_en=user_record["department_en"],
        permissions=user_record["permissions"],
    )
