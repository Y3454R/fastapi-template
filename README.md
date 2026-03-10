# FastAPI Template

A production-ready FastAPI boilerplate with JWT authentication, user management, public asset handling, and a pluggable AI services layer.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async-compatible) |
| Database | PostgreSQL |
| Auth | JWT via `python-jose` + `bcrypt` |
| Migrations | Alembic |
| AI | OpenAI GPT-4o (optional) |
| File Serving | FastAPI `StaticFiles` |

---

## Directory Structure

```
fastapi-template/
│
├── main.py                     # App entry point
├── run.py                      # Uvicorn runner
├── requirements.txt
├── .env.example                # Environment template → copy to .env
├── alembic.ini
│
├── static/                     # Public assets (auto-served at /static/*)
│   ├── images/
│   ├── videos/
│   └── files/
│
├── config/
│   └── database.py             # Engine, session factory, Base
│
├── core/
│   ├── config.py               # Settings (reads from .env)
│   ├── security.py             # bcrypt hashing + JWT encode/decode
│   └── auth.py                 # FastAPI auth dependencies
│
├── models/
│   ├── base.py                 # BaseModel (id, created_at, updated_at)
│   ├── user.py                 # User
│   ├── user_role.py            # UserRole
│   └── item.py                 # Item (example CRUD resource)
│
├── schemas/
│   ├── auth.py                 # LoginRequest, TokenResponse, AuthUserResponse
│   ├── user.py                 # UserCreate, UserUpdate, UserResponse
│   └── item.py                 # ItemCreate, ItemUpdate, ItemResponse
│
├── routers/
│   ├── auth.py                 # POST /api/v1/auth/login, GET /api/v1/auth/me
│   ├── user.py                 # CRUD  /api/v1/users
│   ├── item.py                 # CRUD  /api/v1/items  ← example, clone this
│   ├── assets.py               # POST/DELETE /api/v1/assets
│   └── assets.py               # POST/DELETE /api/v1/assets
│
├── ai/                         # AI Library (OpenAI logic, base interfaces)
│   ├── base.py                 # Abstract AIService interface
│   └── openai_service.py       # OpenAI implementation
├── services/
│
├── db/
│   ├── init.py                 # create_all on startup
│   └── crud.py                 # Shared query helpers
│
├── tests/
│   ├── conftest.py
│   └── services/
│
└── migrations/                 # Alembic migration files
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/your-org/fastapi-template.git
cd fastapi-template
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values (see [Environment Variables](#environment-variables)).

### 3. Run

```bash
# Development (auto-reload)
uvicorn main:app --reload --port 8298

# Or using the bundled runner
python run.py
```

Open the interactive docs at **[http://localhost:8298/docs](http://localhost:8298/docs)**.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | ✅ | `8298` | Server port |
| `APP_NAME` | | `FastAPI Template` | Shown in Swagger UI |
| `API_PREFIX` | ✅ | `/api/v1` | Global route prefix |
| `DEBUG` | | `false` | Enable debug mode |
| `FRONTEND_URL` | ✅ | | Allowed CORS origin |
| `ADMIN_URL` | ✅ | | Allowed CORS origin |
| `DB_USERNAME` | ✅ | | PostgreSQL user |
| `DB_PASSWORD` | ✅ | | PostgreSQL password |
| `DB_HOST` | ✅ | | PostgreSQL host |
| `DB_PORT` | ✅ | | PostgreSQL port |
| `DB_NAME` | ✅ | | PostgreSQL database name |
| `JWT_SECRET_KEY` | ✅ | | Generate: `openssl rand -hex 32` |
| `JWT_ALGORITHM` | ✅ | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | `1440` | Token lifetime (24 h) |
| `STATIC_DIR` | | `static` | Root directory for uploaded files |
| `MAX_UPLOAD_SIZE_MB` | | `10` | Maximum upload size in MB |
| `OPENAI_API_KEY` | | *(blank)* | OpenAI key – leave blank to disable AI routes |

---

## API Overview

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/auth/login` | ❌ | Login with email + password, returns JWT |
| `GET` | `/api/v1/auth/me` | ✅ | Returns the current user's profile |

### Users
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/users/` | ✅ | List all users |
| `GET` | `/api/v1/users/{id}` | ✅ | Get a user by ID |
| `POST` | `/api/v1/users/` | ❌ | Register a new user |
| `DELETE` | `/api/v1/users/{id}` | ✅ | Delete a user |

### Items *(example – replace with your domain)*
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/items/` | ✅ | List items |
| `GET` | `/api/v1/items/{id}` | ✅ | Get an item |
| `POST` | `/api/v1/items/` | ✅ | Create an item |
| `PATCH` | `/api/v1/items/{id}` | ✅ | Update an item |
| `DELETE` | `/api/v1/items/{id}` | ✅ | Soft-delete an item |

### Assets
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/assets/upload` | ✅ | Upload image / video / file |
| `DELETE` | `/api/v1/assets/{sub_dir}/{filename}` | ✅ | Delete an uploaded file |

---

## Public Asset Handling

Uploaded files are stored in `static/<type>/<uuid>.<ext>` and served at `/static/*`.

**Supported upload types:**

| MIME Type | Saved Under |
|-----------|-------------|
| `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/svg+xml` | `static/images/` |
| `video/mp4`, `video/mpeg`, `video/quicktime`, `video/webm` | `static/videos/` |
| `application/pdf`, `text/plain`, `application/zip` | `static/files/` |

**Example – upload an image (cURL):**

```bash
TOKEN="your_jwt_token"
curl -X POST http://localhost:8298/api/v1/assets/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/photo.jpg"
# Response: {"filename": "abc123.jpg", "content_type": "image/jpeg", "url": "/static/images/abc123.jpg"}
```

The returned `url` can be stored in your database and served directly to clients.

---

## AI Services Library

The `ai/` package provides a provider-agnostic interface for AI services. By default, it includes an **OpenAI GPT-4o** implementation. It is designed to be used as a library within your service layer, rather than having its own public API routes.

### Usage Example

```python
from ai.openai_service import openai_service

async def my_business_logic():
    response = await openai_service.chat("Your prompt here")
    print(response)
```

### Add your own AI provider

1. Subclass `AIService` in `ai/base.py`.
2. Implement `chat()` and `analyze_image()`.

```python
# ai/anthropic_service.py
from ai.base import AIService

class AnthropicService(AIService):
    async def chat(self, prompt: str, **kwargs) -> str:
        ...
    async def analyze_image(self, image_url: str, **kwargs) -> str:
        ...
```

---

## Adding a New Resource

The `Item` resource is a ready-to-clone template. To add a new domain entity:

1. **Model** – copy `models/item.py`, rename the class and table.
2. **Schema** – copy `schemas/item.py`, adjust fields.
3. **Service** – copy `services/item.py`, update the model imports.
4. **Router** – copy `routers/item.py`, update the prefix and service calls.
5. **Register** – import in `models/__init__.py` and `routers/__init__.py`, then add to `app.include_router(...)` in `main.py`.

---

## Database Migrations (Alembic)

```bash
# Create a new migration after changing a model
alembic revision --autogenerate -m "add my_table"

# Apply all pending migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1
```

---

## Docker

```bash
# Build
docker build -t fastapi-template .

# Run (pass your .env file)
docker run --env-file .env -p 8298:8298 fastapi-template
```

Or use the provided scripts:

```bash
bash run_docker_local.sh   # local dev
bash run_docker_prod.sh    # production
```


## DB Workflow practice
```
1️⃣ change SQLAlchemy model
2️⃣ alembic revision --autogenerate -m "message"
3️⃣ review migration file
4️⃣ alembic upgrade head
```
