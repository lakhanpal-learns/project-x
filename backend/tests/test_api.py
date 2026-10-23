import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_full_workflow():
    print("--- 1. Testing Health Check ---")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("Health response:", res.json())

    print("\n--- 2. Testing CSRF Token Endpoint ---")
    res = client.get("/api/v1/auth/csrf-token")
    assert res.status_code == 200, f"CSRF token failed: {res.text}"
    csrf_token = res.json()["csrf_token"]
    print("Obtained CSRF Token:", csrf_token[:25] + "...")

    print("\n--- 3. Testing Services Catalog ---")
    res = client.get("/api/v1/services")
    assert res.status_code == 200, f"Get services failed: {res.text}"
    services = res.json()
    assert len(services) >= 4, f"Expected at least 4 services, got {len(services)}"
    print(f"Retrieved {len(services)} services: {[s['name'] for s in services]}")
    service_id = services[0]["id"]

    print("\n--- 4. Testing User Registration ---")
    import uuid
    random_email = f"customer_{uuid.uuid4().hex[:6]}@example.com"
    reg_payload = {
        "full_name": "Test Customer",
        "email": random_email,
        "password": "Password@123",
        "phone": "+1 555-0199",
    }
    res = client.post(
        "/api/v1/auth/register",
        json=reg_payload,
        headers={"X-CSRF-Token": csrf_token},
    )
    assert res.status_code == 201, f"Registration failed: {res.text}"
    print("Registered customer:", res.json()["email"])

    print("\n--- 5. Testing Customer Login ---")
    login_payload = {
        "email": random_email,
        "password": "Password@123",
    }
    res = client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 200, f"Login failed: {res.text}"
    customer_token = res.json()["access_token"]
    print("Customer logged in successfully.")

    print("\n--- 6. Testing /auth/me with Bearer Token ---")
    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert res.status_code == 200, f"/auth/me failed: {res.text}"
    assert res.json()["email"] == random_email
    print("Retrieved profile for:", res.json()["name"])

    print("\n--- 7. Testing Customer Service Request Creation ---")
    request_payload = {
        "service_id": service_id,
        "vehicle_details": "Tesla Model 3 - Midnight Silver",
        "preferred_date": "2026-11-01",
        "preferred_time": "10:00 AM",
        "message": "Please pay extra attention to wheels.",
    }
    res = client.post(
        "/api/v1/requests",
        json=request_payload,
        headers={
            "Authorization": f"Bearer {customer_token}",
            "X-CSRF-Token": csrf_token,
        },
    )
    assert res.status_code == 201, f"Create request failed: {res.text}"
    req_id = res.json()["id"]
    print(f"Created request ID #{req_id} with status '{res.json()['status']}'")

    print("\n--- 8. Testing Customer My Requests List ---")
    res = client.get(
        "/api/v1/requests/my",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert res.status_code == 200, f"Get my requests failed: {res.text}"
    assert len(res.json()) >= 1
    print(f"Customer has {len(res.json())} request(s).")

    print("\n--- 9. Testing Feedback Submission (Automated Email) ---")
    feedback_payload = {
        "name": "Happy Customer",
        "email": random_email,
        "phone": "+1 555-0199",
        "rating": 5,
        "message": "Outstanding car wash service! The car looks brand new.",
    }
    res = client.post(
        "/api/v1/feedback",
        json=feedback_payload,
        headers={"X-CSRF-Token": csrf_token},
    )
    assert res.status_code == 201, f"Feedback submission failed: {res.text}"
    print("Feedback submitted successfully: ID #", res.json()["id"])

    print("\n--- 10. Testing Admin Login ---")
    admin_login = {
        "email": "admin@mrshine.com",
        "password": "Admin@123456",
    }
    res = client.post("/api/v1/auth/login", json=admin_login)
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["access_token"]
    print("Admin logged in successfully.")

    print("\n--- 11. Testing Admin Stats ---")
    res = client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200, f"Admin stats failed: {res.text}"
    stats = res.json()
    print("Admin dashboard stats:", stats)

    print("\n--- 12. Testing Admin Status Update (Approve Request) ---")
    res = client.patch(
        f"/api/v1/admin/requests/{req_id}/status",
        json={"status": "Approved"},
        headers={
            "Authorization": f"Bearer {admin_token}",
            "X-CSRF-Token": csrf_token,
        },
    )
    assert res.status_code == 200, f"Status update failed: {res.text}"
    assert res.json()["status"] == "Approved"
    print(f"Request #{req_id} updated to 'Approved' successfully.")

    print("\n=== ALL 12 TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    test_full_workflow()
