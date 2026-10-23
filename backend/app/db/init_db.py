from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.base import Base, Service, User
from app.db.session import SessionLocal, engine
from app.security import hash_password

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
    """Ensure database tables exist and seed initial data if missing."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # 1. Seed Services
        for svc_data in DEFAULT_SERVICES:
            existing = db.scalars(select(Service).where(Service.name == svc_data["name"])).first()
            if not existing:
                service = Service(**svc_data)
                db.add(service)
                logger.info("Seeded default service: %s", svc_data["name"])

        # 2. Seed Default Accounts
        admin_email = "admin@mrshine.com"
        admin = db.scalars(select(User).where(User.email == admin_email)).first()
        if not admin:
            admin_user = User(
                name="MrShine Administrator",
                email=admin_email,
                phone="+1 (555) 019-2834",
                password_hash=hash_password("Admin@123456"),
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            logger.info("Seeded default admin user: %s (password: Admin@123456)", admin_email)

        customer_email = "customer@mrshine.com"
        customer = db.scalars(select(User).where(User.email == customer_email)).first()
        if not customer:
            customer_user = User(
                name="Demo Customer",
                email=customer_email,
                phone="+1 (555) 010-0200",
                password_hash=hash_password("Customer@123456"),
                role="customer",
                is_active=True,
            )
            db.add(customer_user)
            logger.info("Seeded default customer: %s (password: Customer@123456)", customer_email)

        db.commit()
    logger.info("Database initialization completed.")
