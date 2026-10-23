from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.base import Base, Service, User
from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.security import hash_password, verify_password

logger = get_logger("app.db.init")

DEFAULT_SERVICES = [
    {
        "name": "Exterior Car Wash",
        "description": "Thorough hand wash, wheel shine, rinse, and microfiber drying for a crystal clear finish.",
        "price": Decimal("25.00"),
        "duration_minutes": 30,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Interior Cleaning",
        "description": "Deep vacuuming, dashboard restoration, window streak cleaning, and fabric upholstery refresh.",
        "price": Decimal("45.00"),
        "duration_minutes": 45,
        "image_url": "/assets/images/interior-cleaning.jpg",
    },
    {
        "name": "Complete Cleaning",
        "description": "Full exterior wash combined with complete interior detailing for comprehensive care.",
        "price": Decimal("65.00"),
        "duration_minutes": 75,
        "image_url": "/assets/images/complete-cleaning.jpg",
    },
    {
        "name": "Premium Detailing",
        "description": "Paint decontamination, hand paste wax, ceramic protection spray, leather conditioning, and engine bay wipe down.",
        "price": Decimal("110.00"),
        "duration_minutes": 120,
        "image_url": "/assets/images/premium-detailing.jpg",
    },
]


def init_database() -> None:
    """Ensure database tables exist and seed environment-appropriate initial data."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Seed the public service catalog in every environment.
        for svc_data in DEFAULT_SERVICES:
            existing = db.scalars(select(Service).where(Service.name == svc_data["name"])).first()
            if not existing:
                db.add(Service(**svc_data))
                logger.info("Seeded default service: %s", svc_data["name"])

        default_admin_email = "admin@mrshine.com"
        default_admin_password = "Admin@123456"
        initial_password = settings.ADMIN_INITIAL_PASSWORD or ""
        if initial_password and len(initial_password) < 12:
            logger.error(
                "ADMIN_INITIAL_PASSWORD must be at least 12 characters; production admin bootstrap is disabled."
            )
            initial_password = ""

        if settings.is_production:
            # Migrate an old installation away from the publicly documented development credential.
            legacy_admin = db.scalars(
                select(User).where(User.email == default_admin_email)
            ).first()
            if legacy_admin and verify_password(default_admin_password, legacy_admin.password_hash):
                if initial_password:
                    configured_email = settings.ADMIN_EMAIL.strip().lower()
                    email_owner = db.scalars(
                        select(User).where(User.email == configured_email, User.id != legacy_admin.id)
                    ).first()
                    if not email_owner:
                        legacy_admin.email = configured_email
                    legacy_admin.password_hash = hash_password(initial_password)
                    legacy_admin.is_active = True
                    logger.warning("Rotated the legacy default admin credential during production startup.")
                else:
                    legacy_admin.is_active = False
                    logger.error(
                        "Disabled the legacy default admin account. Set a strong ADMIN_INITIAL_PASSWORD "
                        "deployment secret and restart to bootstrap an administrator."
                    )

            configured_email = settings.ADMIN_EMAIL.strip().lower()
            admin = db.scalars(select(User).where(User.email == configured_email)).first()
            if not admin and initial_password:
                db.add(
                    User(
                        name="MrShine Administrator",
                        email=configured_email,
                        phone=None,
                        password_hash=hash_password(initial_password),
                        role="admin",
                        is_active=True,
                    )
                )
                logger.info("Bootstrapped production administrator from ADMIN_EMAIL.")
            elif not admin:
                logger.warning(
                    "No production administrator was seeded. Configure ADMIN_INITIAL_PASSWORD "
                    "as a deployment secret to bootstrap one."
                )
        else:
            # These credentials are for local development only and must never be used in production.
            admin = db.scalars(select(User).where(User.email == default_admin_email)).first()
            if not admin:
                db.add(
                    User(
                        name="MrShine Administrator",
                        email=default_admin_email,
                        phone="+1 (555) 019-2834",
                        password_hash=hash_password(default_admin_password),
                        role="admin",
                        is_active=True,
                    )
                )
                logger.info("Seeded development admin account: %s", default_admin_email)

            customer_email = "customer@mrshine.com"
            customer = db.scalars(select(User).where(User.email == customer_email)).first()
            if not customer:
                db.add(
                    User(
                        name="Demo Customer",
                        email=customer_email,
                        phone="+1 (555) 010-0200",
                        password_hash=hash_password("Customer@123456"),
                        role="customer",
                        is_active=True,
                    )
                )
                logger.info("Seeded development demo customer: %s", customer_email)

        db.commit()
    logger.info("Database initialization completed.")
