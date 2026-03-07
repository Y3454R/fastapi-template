# API Writing Guidelines

This document defines the conventions and best practices for writing API endpoints in `jogfol-be`. All contributors should follow these guidelines to keep the codebase consistent and maintainable.

---

## Project Structure

API-related code is organized across three layers:

| Layer | Directory | Responsibility |
|---|---|---|
| Router | `routers/` | Define routes, validate input, return responses |
| Service | `services/` | Business logic, validation rules, DB operations |
| Schema | `schemas/` | Request/response shape definitions (Pydantic) |

---

## Routers

Routers live in `routers/<domain>.py` and should be **thin**. They must not contain business logic.

```python
# routers/user.py
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return user_service.get_user(user_id, db)
```

**Rules:**
- Each router uses a consistent URL prefix: `/api/v1/<domain>`
- Always specify `response_model` on each route decorator
- Use `status.HTTP_201_CREATED` for `POST` creation endpoints
- Use `status.HTTP_204_NO_CONTENT` for `DELETE` endpoints, returning `None`
- Auth dependencies (`get_current_active_user`) belong in the router, not the service
- Never import models or perform DB queries directly in a router

---

## Services

Services live in `services/<domain>.py` and contain all business logic.

```python
# services/user.py
def get_user(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
```

**Rules:**
- Each service function takes a `db: Session` as its last parameter
- Return the ORM model object directly — the router's `response_model` handles serialization
- Raise `HTTPException` (not a custom class) with a meaningful `detail` message
- Use standard HTTP status codes (`404`, `400`, `403`, etc.)
- Do not import the router or reference FastAPI request/response types

---

## Schemas

Schemas live in `schemas/<domain>.py` and use Pydantic models.

**Naming Convention:**

| Purpose | Suffix | Example |
|---|---|---|
| Creating a resource | `Create` | `UserCreate` |
| Updating a resource | `Update` | `UserUpdate` |
| API response | `Response` | `UserResponse` |

**Rules:**
- Always add `model_config = ConfigDict(from_attributes=True)` to `Response` schemas
- Use `EmailStr` for email fields
- Use `int | None` instead of `Optional[int]` for optional fields (Python 3.10+)

---

## Authentication

- Protected routes use `Depends(get_current_active_user)` imported from `core.auth`
- If the current user is needed in the service (e.g., `author_id`), pass it explicitly as a parameter — do not pass the full request or dependency

```python
# router passes the user's id to the service
blog_service.create_post(payload, current_user.id, db)
```

---

## Adding a New Feature

1. Define request/response schemas in `schemas/<domain>.py`
2. Write business logic in `services/<domain>.py`
3. Add the route in `routers/<domain>.py` that delegates to the service
4. Register the router in `main.py` with `app.include_router(...)`
