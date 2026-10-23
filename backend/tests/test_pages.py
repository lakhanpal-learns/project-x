from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_landing_page_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "MrShine" in response.text


def test_public_pages_are_served():
    paths = [
        "/pages/login.html",
        "/pages/register.html",
        "/pages/services.html",
        "/pages/request-service.html",
        "/pages/my-requests.html",
        "/pages/admin.html",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200, f"{path}: {response.status_code}"
        assert "text/html" in response.headers["content-type"]


def test_frontend_static_assets_are_served():
    paths = [
        "/css/style.css",
        "/css/responsive.css",
        "/js/api.js",
        "/js/auth.js",
        "/js/main.js",
        "/js/navigation.js",
        "/assets/images/hero-black-car.jpg",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200, f"{path}: {response.status_code}"
