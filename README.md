# MrShine Car Wash & Detailing — Management Platform

A modern, secure web application and RESTful backend for **MrShine Car Wash & Detailing**. Built with FastAPI, SQLAlchemy 2.0, PostgreSQL (hosted on Render), and a responsive vanilla frontend.

---

## Features

- **Customer Authentication**: Secure customer registration and login powered by **Argon2** password hashing and **JWT** tokens.
- **CSRF Protection & Security**: Signed cryptographic CSRF tokens, strict origin/header checks, and FastAPI Dependency Injection (DI) guards.
- **Service Request Workflow**: Authenticated customers can browse service packages, choose custom dates and times, and submit requests with instant status tracking.
- **Automated Email Notifications**: Automatic email confirmation for customers and notifications for administrators upon service booking, status updates, and feedback submission.
- **Admin Management Portal**: Real-time stats dashboard (total, pending, approved, rejected requests) and one-click request approval/rejection.
- **Modular Global Error Handling**: Centralized exception hierarchy (`AppException`, `BadRequestError`, `UnauthorizedError`, `ConflictError`, `CSRFValidationError`) with structured JSON error responses.
- **Structured Logging**: Replaces raw console logging with structured, timestamped log formatters across all modules.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.12+, FastAPI, Uvicorn, Pydantic v2, `pydantic-settings` |
| **Database & ORM**| PostgreSQL, SQLAlchemy 2.0, `psycopg` (v3 binary), Alembic |
| **Security** | `pwdlib[argon2]`, `python-jose` (JWT), HMAC-SHA256 CSRF protection |
| **Notifications** | Automated SMTP email delivery with background task queuing |
| **Frontend** | HTML5, CSS3 (Custom Properties & Responsive Grid), Modern Vanilla JavaScript |

---

## Project Structure

```
project-x/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py         # Login, register, me, csrf-token
│   │   │       ├── services.py     # Service catalog
│   │   │       ├── requests.py     # Service requests (submit & customer list)
│   │   │       ├── feedback.py     # Customer feedback & automated emails
│   │   │       ├── admin.py        # Admin stats & request status updates
│   │   │       └── router.py       # Aggregated v1 API router
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic BaseSettings (dev vs prod)
│   │   │   ├── errors.py           # Global error handler & modular exceptions
│   │   │   └── logging.py          # Structured standard logging
│   │   ├── db/
│   │   │   ├── session.py          # Engine, sessionmaker, test_db_connection
│   │   │   ├── base.py             # DeclarativeBase with all model metadata
│   │   │   └── init_db.py          # Table creation and default seed data
│   │   ├── models/                 # SQLAlchemy 2.0 ORM models
│   │   │   ├── user.py             # User (customer / admin)
│   │   │   ├── service.py          # Car wash services catalog
│   │   │   ├── request.py          # Customer service requests
│   │   │   └── feedback.py         # Inquiries and feedback
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── security/               # Dedicated security module
│   │   │   ├── passwords.py        # Argon2 hashing & verification
│   │   │   ├── tokens.py           # JWT access token creation & decode
│   │   │   ├── csrf.py             # CSRF generation and header validation
│   │   │   └── dependencies.py     # FastAPI DI (get_current_user, get_current_admin)
│   │   ├── services/
│   │   │   └── email.py            # Automated SMTP emails
│   │   └── main.py                 # FastAPI application root & static mounts
│   ├── tests/
│   │   └── test_api.py             # End-to-end API test suite
│   ├── .env                        # Local environment variables
│   └── pyproject.toml              # Dependencies & project metadata
├── frontend/
│   ├── css/                        # Global & responsive styles
│   ├── js/
│   │   ├── api.js                  # Centralized API client (auth & CSRF)
│   │   └── auth.js                 # Session management & route protection
│   ├── pages/
│   │   ├── login.html              # Customer & admin login
│   │   ├── register.html           # Customer registration
│   │   ├── services.html           # Service catalog & pricing
│   │   ├── request-service.html    # Book service & feedback form
│   │   ├── my-requests.html        # Customer dashboard
│   │   └── admin.html              # Administrator dashboard
│   └── index.html                  # Landing page
└── docs/
    ├── architecture.md             # System & security architecture
    ├── database-schema.md          # Database schema reference
    ├── deploy.md                   # Render production deployment guide
    └── requirements.md             # Functional requirements
```

---

## Quickstart

### 1. Prerequisites
- Python 3.12+
- `uv` package manager (`pip install uv` or standalone installer)

### 2. Environment Variables
Create or verify `backend/.env`:
```env
APP_ENV=development
DATABASE_URL=postgresql://mrshine_db_user:PASSWORD@HOST/mrshine_db
SECRET_KEY=your-jwt-secret-key-change-in-production
CSRF_SECRET_KEY=your-csrf-secret-key-change-in-production

# Optional SMTP Settings for Live Email Delivery
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_TLS=True
EMAILS_FROM_EMAIL=notifications@mrshine.com
ADMIN_EMAIL=admin@mrshine.com
```

> **Note**: In development mode or if SMTP credentials are blank, email sending is safely logged to the console/logger without failing user requests.

### 3. Run the Backend
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```
- Open browser at `http://localhost:8000` to view the website.
- Interactive API Docs: `http://localhost:8000/docs`.

### 4. Seeded Accounts and Production Admin Setup

Default admin and demo-customer accounts are created only when `APP_ENV` is not `production`. For production, configure a strong `ADMIN_INITIAL_PASSWORD` deployment secret (at least 12 characters) and `ADMIN_EMAIL` before the first startup. The app will use these to bootstrap the administrator and rotate a legacy account only when it still has the published development password. If the initial password is not configured, a legacy account still using the development password is disabled rather than left exposed.
- **Development admin only**: `admin@mrshine.com` / `Admin@123456` (never use these credentials in production).
- **Development demo customer**: `customer@mrshine.com` / `Customer@123456` (development only).
- **Customer**: Register any new account through `/register.html`.

### 5. Running Tests
```bash
cd backend
uv run python tests/test_api.py
```
All 12 end-to-end tests verify health check, CSRF tokens, registration, login, JWT verification, service request booking, feedback submission, automated email queueing, and admin status updates.
