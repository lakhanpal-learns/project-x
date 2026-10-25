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
        "name": "Saloon Car Wash Interior–Exterior",
        "description": "Interior and exterior wash for saloon cars.",
        "price": Decimal("15.00"),
        "duration_minutes": 45,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Saloon Car Hand Wash Interior–Exterior",
        "description": "Hand wash for the interior and exterior of saloon cars. Available Monday to Thursday.",
        "price": Decimal("20.00"),
        "duration_minutes": 60,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Saloon Car Wash Exterior",
        "description": "Exterior wash for saloon cars.",
        "price": Decimal("11.00"),
        "duration_minutes": 30,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Saloon Car Hand Wash Exterior",
        "description": "Exterior hand wash for saloon cars. Available Monday to Thursday.",
        "price": Decimal("16.00"),
        "duration_minutes": 35,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Van Car Wash Interior–Exterior",
        "description": "Interior and exterior wash for vans.",
        "price": Decimal("17.00"),
        "duration_minutes": 60,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Van Car Wash Exterior",
        "description": "Exterior wash for vans.",
        "price": Decimal("12.00"),
        "duration_minutes": 35,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Taxi Interior–Exterior",
        "description": "Interior and exterior wash for taxis.",
        "price": Decimal("11.00"),
        "duration_minutes": 45,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Taxi Exterior",
        "description": "Exterior wash for taxis.",
        "price": Decimal("9.00"),
        "duration_minutes": 25,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Interior Detailing SUV",
        "description": "Interior detailing for SUVs. Available by appointment.",
        "price": Decimal("140.00"),
        "duration_minutes": 180,
        "image_url": "/assets/images/interior-cleaning.jpg",
    },
    {
        "name": "Interior Detailing Saloon",
        "description": "Interior detailing for saloon cars. Available by appointment.",
        "price": Decimal("120.00"),
        "duration_minutes": 150,
        "image_url": "/assets/images/interior-cleaning.jpg",
    },
    {
        "name": "Car Seats Cleaning",
        "description": "Professional car seat cleaning. Available by appointment.",
        "price": Decimal("50.00"),
        "duration_minutes": 60,
        "image_url": "/assets/images/interior-cleaning.jpg",
    },
    {
        "name": "Headlights Restoration",
        "description": "Headlight restoration service. Available by appointment.",
        "price": Decimal("30.00"),
        "duration_minutes": 60,
        "image_url": "/assets/images/exterior-wash.jpg",
    },
    {
        "name": "Exterior Detailing",
        "description": "Detailed exterior treatment. Available by appointment.",
        "price": Decimal("160.00"),
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
