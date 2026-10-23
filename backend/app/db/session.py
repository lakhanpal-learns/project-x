
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.engine import make_url

# Load backend/.env regardless of the current terminal directory
BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing from backend/.env")

# Use the installed Psycopg 3 driver
url = make_url(database_url)

if url.drivername in ("postgres", "postgresql"):
    url = url.set(drivername="postgresql+psycopg")

# Require an encrypted connection to the hosted database
if "sslmode" not in url.query:
    url = url.update_query_dict({"sslmode": "require"})

engine = create_engine(
    url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """Provide a database session to an API endpoint."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_connection():
    """Check whether PostgreSQL is reachable."""
    with engine.connect() as connection:
        return connection.execute(text("SELECT 1")).scalar_one()
