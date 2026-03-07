# Test Writing Guidelines

This document defines conventions for writing unit tests in `jogfol-be`. Tests live in `tests/` and cover the `services/` layer.

---

## Structure

```
tests/
├── conftest.py          # Shared fixtures
└── services/
    ├── test_auth.py
    ├── test_user.py
    └── test_blog.py
```

Each file in `services/` has a corresponding test file in `tests/services/`.

---

## Running Tests

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

---

## Fixtures (`conftest.py`)

Shared fixtures are defined in `tests/conftest.py` and available automatically to all test files.

| Fixture | What it provides |
|---|---|
| `mock_db` | A `MagicMock` simulating a SQLAlchemy `Session` |
| `mock_user` | A `MagicMock` with sensible default user attributes |
| `mock_post` | A `MagicMock` with sensible default post attributes |

Use these fixtures instead of creating inline mocks in each test.

---

## Writing Tests

### Group tests by function using classes

```python
class TestCreateUser:
    def test_raises_400_on_duplicate_email(self, mock_db, mock_user): ...
    def test_creates_and_returns_user(self, mock_db): ...
```

Use a class per service function. Name the class `Test<FunctionName>`.

### Mock the DB with `MagicMock`

Never connect to a real database. Chain `.return_value` to simulate SQLAlchemy query chains:

```python
# Simulates: db.query(User).filter(...).first()
mock_db.query.return_value.filter.return_value.first.return_value = mock_user
```

To test multiple sequential calls (e.g., email then username check), use `side_effect`:

```python
mock_db.query.return_value.filter.return_value.first.side_effect = [None, mock_user]
```

### Patch external dependencies with `unittest.mock.patch`

Any function imported inside a service must be patched at its **service-level path**, not the source module:

```python
# Correct: patch where it's USED
with patch("services.auth.verify_password", return_value=False):
    ...

# Wrong: patch where it's DEFINED
with patch("core.security.verify_password", return_value=False):
    ...
```

### Assert HTTP errors by status code

```python
with pytest.raises(HTTPException) as exc_info:
    get_user(99, mock_db)

assert exc_info.value.status_code == 404
```

Always assert the `status_code`, not the `detail` string (detail messages can change).  
For `400` errors where multiple conditions exist (e.g., duplicate email vs username), also assert the `detail` to differentiate them.

### Assert DB side effects for write operations

For `create` and `delete` functions, verify the DB was actually mutated:

```python
mock_db.add.assert_called_once()
mock_db.commit.assert_called_once()

mock_db.delete.assert_called_once_with(mock_user)
mock_db.commit.assert_called_once()
```

---

## Checklist: What to Test Per Service Function

| Function type | Required test cases |
|---|---|
| `get_*` (single) | Found case, 404 case |
| `get_*` (list) | Returns list |
| `create_*` | Happy path, each uniqueness violation |
| `delete_*` | Happy path, 404 case, 403 case (if applicable) |
| Auth | Invalid credentials (401), inactive user (403), success |
