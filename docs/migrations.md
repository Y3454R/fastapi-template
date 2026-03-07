# Database & Migration Guidelines

This project uses **SQLAlchemy 2.0** (Mapped/mapped_column syntax) and **Alembic** for schema migrations.

---

## 🏗️ Model Architecture

To prevent circular imports and maintain a modular structure, we follow two strict rules:

1. **String References:** Always use strings for relationship targets (e.g., `relationship("Project", ...)`).
2. **Lazy Type Hinting:** Use `TYPE_CHECKING` blocks to import models for IDE autocomplete without loading them at runtime.

---

## 🚀 The Migration Workflow

Follow these steps whenever you modify a file in the `models/` directory.

### 1. Update the Models

Make your changes (add columns, new tables, etc.). Ensure any new model is imported in `models/__init__.py`.

### 2. Generate a Revision

Run the autogenerate command to let Alembic compare your code to the database.

```bash
alembic revision --autogenerate -m "describe your changes here"
```

### 3. Review the Script

Check the generated file in `migrations/versions/`. Ensure it captures:

- Added/Removed columns.
- New Foreign Key constraints.
- Indexes and Unique constraints.

### 4. Apply Changes

Push the changes to your local PostgreSQL instance.

```bash
alembic upgrade head
```

---

## 🛠️ Common Commands

| Task | Command |
|---|---|
| Check Current Version | `alembic current` |
| View History | `alembic history --verbose` |
| Undo Last Migration | `alembic downgrade -1` |
| Wipe and Reset | `alembic downgrade base` *(Careful! Deletes data)* |

---

## 📝 Field Specifics

### Markdown Content

All long-form text (Project descriptions, Blog content) is stored using the `Text` type.

- **Database:** `content: Mapped[str] = mapped_column(Text)`
- **Rendering:** The frontend is responsible for parsing the raw Markdown string into HTML.

### UUIDs

We use UUID4 for public-facing identifiers to prevent ID enumeration. These are generated via Python's `uuid` module at the time of insertion.

---

## ⚠️ Troubleshooting

- **Empty Migration:** If `upgrade()` is empty, ensure the model is imported in `models/__init__.py`.
- **ImportError:** Ensure you aren't using `from models.x import Y` at the top level of your model files; use the `TYPE_CHECKING` pattern.