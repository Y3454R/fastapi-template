from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import settings
from db.init import init_db
from routers import auth, user, assets, item

# ---------------------------------------------------------------------------
# OpenAPI metadata
# ---------------------------------------------------------------------------
_DESCRIPTION = """
## FastAPI Template 🚀

A production-ready FastAPI boilerplate with:

- 🔐 **JWT authentication** – register, login, refresh
- 👤 **User management** (CRUD with roles)
- 📦 **Item resource** – example CRUD pattern to clone for your domain
- 🖼️ **Asset upload** – images, videos, and files served via `/static`
- 🖼️ **Asset upload** – images, videos, and files served via `/static`

> **Interactive docs**: [/docs](/docs) &nbsp;|&nbsp; **ReDoc**: [/redoc](/redoc)
"""

_TAGS_METADATA = [
    {
        "name": "auth",
        "description": "Authentication endpoints – login and retrieve the current user.",
    },
    {
        "name": "users",
        "description": "User management: create, list, retrieve, and delete users.",
    },
    {
        "name": "items (example)",
        "description": (
            "Example CRUD resource. Clone this module (model → schema → service → router) "
            "as the starting point for your own domain entities."
        ),
    },
    {
        "name": "assets",
        "description": (
            "Upload images, videos, and files to the public `static/` directory. "
            "Uploaded files are served at `/static/<type>/<filename>`."
        ),
    },
]


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialise the database on startup."""
    init_db()
    yield


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    description=_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=_TAGS_METADATA,
    contact={
        "name": "Template Maintainer",
        "url": "https://github.com/your-org/fastapi-template",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
# Ensure the static directory exists at startup so the mount never fails
Path(settings.static_dir).mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

# ---------------------------------------------------------------------------
# CORS middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(item.router)
app.include_router(assets.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Returns `{\"status\": \"ok\"}` when the service is up.",
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}