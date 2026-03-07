# scripts/seed/users.py
from config.database import SessionLocal
from models.user import User
from models.related import UserRole
import bcrypt


def seed_superadmin():
    db = SessionLocal()
    try:
        username = "superadmin"
        email = "[EMAIL_ADDRESS]"

        if db.query(User).filter_by(username=username).first():
            print("Superadmin user already exists, skipping...")
            return

        role = db.query(UserRole).filter_by(name="super_admin").first()
        if not role:
            print("Role 'super_admin' does not exist. Please seed roles first.")
            return

        password = "[PASSWORD]"
        # bcrypt.hashpw expects bytes.
        # It handles the 72-character limit and salt generation internally.
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        user = User(
            full_name="Super Admin",
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        print(f"User '{username}' created.")
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")
    finally:
        db.close()
