
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="MrShine Car Wash API",
    version="1.0.0",
    description="Backend for the MrShine Car Wash website",
)

# Project root: project/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Serve frontend assets and pages
app.mount(
    "/css",
    StaticFiles(directory=FRONTEND_DIR / "css"),
    name="css",
)

app.mount(
    "/js",
    StaticFiles(directory=FRONTEND_DIR / "js"),
    name="javascript",
)

app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_DIR / "assets"),
    name="assets",
)

app.mount(
    "/pages",
    StaticFiles(directory=FRONTEND_DIR / "pages"),
    name="pages",
)


@app.get("/", include_in_schema=False)
def home():
    """Serve the MrShine landing page."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/login.html", include_in_schema=False)
def login_page():
    """Serve the MrShine login page."""
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
