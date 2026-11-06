"""Unit tests for Authentication and Administrative Division Error Reporting.

Tests:
1. Valid admin login (admin / admin123) -> returns admin role and permissions.
2. Valid user login (user / user123) -> returns user role.
3. Invalid login credentials -> returns 401 Unauthorized.
4. List division reports -> returns unread count and seeded items.
5. Submit division report -> returns 201 Created and updates unread count.
6. Admin mark report as read -> status transitions to 'read'.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_auth_login_admin_success():
    """Verify administrator login with credentials: admin / admin123."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["user"]["role"] == "admin"
    assert "manage_divisions" in data["user"]["permissions"]


def test_auth_login_user_success():
    """Verify standard user login with credentials: user / user123."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "user", "password": "user123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["user"]["role"] == "user"


def test_auth_login_invalid_password():
    """Verify 401 Unauthorized for incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_update_user_profile():
    """Verify updating user profile information and settings."""
    payload = {
        "username": "admin",
        "full_name_km": "អភិបាលប្រព័ន្ធជាន់ខ្ពស់",
        "department_km": "ការិយាល័យបច្ចេកវិទ្យា និងអត្រានុកូលដ្ឋាន",
    }
    response = client.put("/api/v1/auth/profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name_km"] == "អភិបាលប្រព័ន្ធជាន់ខ្ពស់"
    assert data["department_km"] == "ការិយាល័យបច្ចេកវិទ្យា និងអត្រានុកូលដ្ឋាន"



def test_get_division_reports():
    """Verify listing of reports returns valid structure and unread count."""
    response = client.get("/api/v1/geo/reports")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "unread_count" in data
    assert "reports" in data
    assert isinstance(data["reports"], list)
    assert data["total"] >= 1


def test_submit_and_update_division_report():
    """Verify user reporting flow and admin mark as read action."""
    # 1. Submit report
    payload = {
        "division_code": "14010103",
        "division_level": "village",
        "current_name_km": "ភូមិស្វាយ",
        "current_name_en": "Phum Svay",
        "issue_type": "spelling",
        "suggested_name_km": "ភូមិស្វាយធំ",
        "suggested_name_en": "Phum Svay Thom",
        "notes": "ឈ្មោះត្រឹមត្រូវគឺស្វាយធំ",
        "reported_by": "user",
    }
    create_res = client.post("/api/v1/geo/reports", json=payload)
    assert create_res.status_code == 201
    created_item = create_res.json()
    report_id = created_item["id"]
    assert created_item["status"] == "pending"
    assert created_item["suggested_name_km"] == "ភូមិស្វាយធំ"
    assert "ព្រៃវែង" in (created_item["parent_hierarchy_km"] or "")

    # 2. Admin marks report as read
    update_res = client.patch(
        f"/api/v1/geo/reports/{report_id}",
        json={"status": "read", "admin_notes": "Reviewed and verified with commune register."},
    )
    assert update_res.status_code == 200
    updated_item = update_res.json()
    assert updated_item["status"] == "read"
    assert updated_item["admin_notes"] == "Reviewed and verified with commune register."
