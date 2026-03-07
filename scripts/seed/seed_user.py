#!/usr/bin/env python3
"""
Interactive script to seed a user into the database.
Can be run from anywhere:
  python scripts/seed/seed_user.py
  python seed_user.py  (from scripts/seed/)
"""

import sys
import getpass
from pathlib import Path
from dotenv import load_dotenv

# Anchor to jogfol-be/ regardless of where the script is invoked from.
# __file__ = .../jogfol-be/scripts/seed/seed_user.py -> parents[2] = jogfol-be/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env explicitly from the project root BEFORE importing anything
# that touches os.getenv() at module level (config/database.py, core/config.py)
load_dotenv(PROJECT_ROOT / ".env")

import bcrypt
from config.database import SessionLocal
from models.user import User
from models.user_role import UserRole


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def prompt(label: str, default: str = "", required: bool = True) -> str:
    hint = f" [{default}]" if default else ""
    while True:
        value = input(f"{label}{hint}: ").strip()
        if not value and default:
            return default
        if value or not required:
            return value
        print(f"  '{label}' is required.")


def prompt_password() -> str:
    while True:
        pwd = getpass.getpass("Password: ")
        if len(pwd) < 8:
            print("  Password must be at least 8 characters.")
            continue
        confirm = getpass.getpass("Confirm password: ")
        if pwd == confirm:
            return pwd
        print("  Passwords do not match. Try again.")


def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def choose_role(db) -> object:
    roles = db.query(UserRole).all()
    if not roles:
        print("\nError: No roles found in the database. Please seed roles first.")
        sys.exit(1)

    print("\nAvailable roles:")
    for i, role in enumerate(roles, start=1):
        print(f"  {i}. {role.name}")

    while True:
        raw = input("\nSelect role number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(roles):
            return roles[int(raw) - 1]
        print("  Invalid selection. Enter a number from the list.")


def confirm(message: str) -> bool:
    return input(f"\n{message} [y/N]: ").strip().lower() == "y"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def seed_user():
    print("=" * 50)
    print("  Interactive User Seeder")
    print("=" * 50)
    print("\nEnter the new user's details (Ctrl+C to cancel).\n")

    full_name = prompt("Full name")
    username  = prompt("Username")
    email     = prompt("Email")
    is_active = confirm("Set user as active?")
    print("")
    password  = prompt_password()

    db = SessionLocal()
    try:
        if db.query(User).filter_by(username=username).first():
            print(f"\nError: Username '{username}' already exists.")
            return

        if db.query(User).filter_by(email=email).first():
            print(f"\nError: Email '{email}' already exists.")
            return

        role = choose_role(db)

        print("\n--- Summary ---")
        print(f"  Full name : {full_name}")
        print(f"  Username  : {username}")
        print(f"  Email     : {email}")
        print(f"  Role      : {role.name}")
        print(f"  Active    : {is_active}")

        if not confirm("Create this user?"):
            print("\nAborted. No changes were made.")
            return

        user = User(
            full_name=full_name,
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_active=is_active,
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        print(f"\nUser '{username}' created successfully.")

    except Exception as e:
        db.rollback()
        print(f"\nError creating user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed_user()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
