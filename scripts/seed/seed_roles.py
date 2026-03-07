# scripts/seed/roles.py
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from config.database import SessionLocal
from models.user_role import UserRole


def seed_roles():
    roles = ["super_admin", "admin", "user"]
    db = SessionLocal()
    try:
        for r in roles:
            if not db.query(UserRole).filter_by(name=r).first():
                db.add(UserRole(name=r))
        db.commit()
        print("Roles seeded.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding roles: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()
