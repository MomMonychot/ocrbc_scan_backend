"""Authentication and User Authorization Schemas.

Architectural and Security Rationale:
- Strongly-typed Pydantic v2 schemas for role-based authentication.
- Strict snake_case naming conventions throughout.
- Supports both Administrative System Admin ('admin') and Civil Status Officer ('user') roles.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Payload for user and administrator login."""

    username: str = Field(..., description="System username", examples=["admin", "user"])
    password: str = Field(..., description="Authentication secret", examples=["admin123", "user123"])


class UserProfile(BaseModel):
    """Authenticated user profile representation."""

    username: str = Field(..., examples=["admin"])
    role: str = Field(..., description="User role: 'admin' or 'user'", examples=["admin"])
    full_name_km: str = Field(..., examples=["អភិបាលប្រព័ន្ធរដ្ឋបាល"])
    full_name_en: str = Field(..., examples=["System Administrator"])
    department_km: str = Field(..., examples=["ការិយាល័យអត្រានុកូលដ្ឋាន និងអត្តសញ្ញាណប័ណ្ណ"])
    department_en: str = Field(..., examples=["Civil Registration and Identification Bureau"])
    permissions: List[str] = Field(default_factory=list, examples=[["manage_divisions", "review_reports"]])


class LoginResponse(BaseModel):
    """Standardized authentication response payload."""

    access_token: str = Field(..., examples=["mock_sec_token_admin_2026"])
    token_type: str = Field(default="bearer", examples=["bearer"])
    user: UserProfile
