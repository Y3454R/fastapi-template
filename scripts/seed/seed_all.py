# scripts/seed/seed_all.py
"""
Seed the database with initial data.

Run from the project root:
    python -m scripts.seed.seed_all
"""
from .roles import seed_roles
from .users import seed_superadmin

if __name__ == "__main__":
    seed_roles()  # roles first
    seed_superadmin()  # then user
