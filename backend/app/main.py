from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import get_logger, setup_logging
from app.db.init_db import init_database
from app.db.session import test_db_connection

# Initialize logging system
setup_logging()
logger = get_logger("app.main")

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown tasks."""
    logger.info("Starting up %s (env: %s)...", settings.PROJECT_NAME, settings.APP_ENV)
    try:
        init_database()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.exception("Failed to initialize database on startup: %s", exc)

    yield

    logger.info("Shutting down %s...", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="Backend for MrShine Car Wash & Detailing Management System",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Register uniform global error handlers
register_error_handlers(app)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_v1_router, prefix="/api")

# Serve frontend static assets
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="javascript")
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    app.mount("/pages", StaticFiles(directory=FRONTEND_DIR / "pages"), name="pages")


# Clean Browser Routing (supports both clean URLs e.g. /admin and legacy .html URLs)
@app.get("/", include_in_schema=False)
def home_page():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/login", include_in_schema=False)
@app.get("/login.html", include_in_schema=False)
def login_page():
    return FileResponse(FRONTEND_DIR / "pages" / "login.html")


@app.get("/register", include_in_schema=False)
@app.get("/register.html", include_in_schema=False)
def register_page():
    return FileResponse(FRONTEND_DIR / "pages" / "register.html")


@app.get("/services", include_in_schema=False)
@app.get("/services.html", include_in_schema=False)
def services_page():
    return FileResponse(FRONTEND_DIR / "pages" / "services.html")


@app.get("/request-service", include_in_schema=False)
@app.get("/book", include_in_schema=False)
@app.get("/request-service.html", include_in_schema=False)
def request_service_page():
    return FileResponse(FRONTEND_DIR / "pages" / "request-service.html")


@app.get("/my-requests", include_in_schema=False)
@app.get("/tracking", include_in_schema=False)
@app.get("/my-requests.html", include_in_schema=False)
def my_requests_page():
    return FileResponse(FRONTEND_DIR / "pages" / "my-requests.html")


@app.get("/admin", include_in_schema=False)
@app.get("/admin.html", include_in_schema=False)
def admin_page():
    return FileResponse(FRONTEND_DIR / "pages" / "admin.html")


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint verifying system and database status."""
    db_ok = False
    try:
        db_ok = test_db_connection() == 1
    except Exception as exc:
        logger.error("Health check DB probe failed: %s", exc)

    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
    }
