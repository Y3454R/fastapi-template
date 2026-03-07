from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from schemas.user import UserCreate
from services.user import create_user, delete_user, get_user, get_users


class TestGetUsers:
    def test_returns_all_users(self, mock_db, mock_user):
        mock_db.query.return_value.all.return_value = [mock_user]
        result = get_users(mock_db)
        assert result == [mock_user]


class TestGetUser:
    def test_returns_user_when_found(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        result = get_user(1, mock_db)
        assert result == mock_user

    def test_raises_404_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            get_user(99, mock_db)
        assert exc_info.value.status_code == 404


class TestCreateUser:
    def _make_payload(self, **kwargs):
        defaults = dict(
            full_name="New User",
            username="newuser",
            email="new@example.com",
            password="[PASSWORD]",
            is_active=True,
            role_id=None,
        )
        return UserCreate(**{**defaults, **kwargs})

    def test_raises_400_on_duplicate_email(self, mock_db, mock_user):
        # First query (email check) returns a user
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        with pytest.raises(HTTPException) as exc_info:
            create_user(self._make_payload(), mock_db)
        assert exc_info.value.status_code == 400
        assert "Email" in exc_info.value.detail

    def test_raises_400_on_duplicate_username(self, mock_db, mock_user):
        # First call (email) returns None, second call (username) returns a user
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, mock_user]
        with pytest.raises(HTTPException) as exc_info:
            create_user(self._make_payload(), mock_db)
        assert exc_info.value.status_code == 400
        assert "Username" in exc_info.value.detail

    def test_creates_and_returns_user(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.refresh.side_effect = lambda u: None
        with patch("services.user.hash_password", return_value="hashed_pw"):
            result = create_user(self._make_payload(), mock_db)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestDeleteUser:
    def test_deletes_user_successfully(self, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        delete_user(1, mock_db)
        mock_db.delete.assert_called_once_with(mock_user)
        mock_db.commit.assert_called_once()

    def test_raises_404_when_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            delete_user(99, mock_db)
        assert exc_info.value.status_code == 404
