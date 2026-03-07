from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_db():
    """Return a MagicMock that mimics a SQLAlchemy Session."""
    return MagicMock()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.full_name = "Test User"
    user.username = "testuser"
    user.email = "test@example.com"
    user.hashed_password = "hashed_secret"
    user.is_active = True
    user.role_id = None
    return user


@pytest.fixture
def mock_post():
    post = MagicMock()
    post.id = 1
    post.title = "Test Post"
    post.content = "Some content"
    post.author_id = 1
    post.category_id = None
    return post
