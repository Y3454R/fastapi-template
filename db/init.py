from config.database import Base, engine

# This "wakes up" all your models so Base.metadata knows they exist
from models import *  # noqa: F401,F403


def init_db() -> None:
    """
    Creates all tables in the database.
    Note: If you are using Alembic, you usually run 'alembic upgrade head'
    instead of this function for production environments.
    """
    Base.metadata.create_all(bind=engine)
