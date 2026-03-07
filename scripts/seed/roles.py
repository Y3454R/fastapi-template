# scripts/seed/roles.py
from config.database import SessionLocal
from models.related import UserRole


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
