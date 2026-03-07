from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from schemas.auth import LoginRequest
from services.auth import authenticate_user


class TestAuthenticateUser:
    def _make_payload(self, email="test@example.com", password="secret"):
        return LoginRequest(email=email, password=password)

    def test_raises_401_when_user_not_found(self, mock_db):
        with patch("services.auth.get_user_by_email", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_user(self._make_payload(), mock_db)
        assert exc_info.value.status_code == 401

    def test_raises_401_on_wrong_password(self, mock_db, mock_user):
        with (
            patch("services.auth.get_user_by_email", return_value=mock_user),
            patch("services.auth.verify_password", return_value=False),
        ):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_user(self._make_payload(), mock_db)
        assert exc_info.value.status_code == 401

    def test_raises_403_when_user_inactive(self, mock_db, mock_user):
        mock_user.is_active = False
        with (
            patch("services.auth.get_user_by_email", return_value=mock_user),
            patch("services.auth.verify_password", return_value=True),
        ):
            with pytest.raises(HTTPException) as exc_info:
                authenticate_user(self._make_payload(), mock_db)
        assert exc_info.value.status_code == 403

    def test_returns_token_response_on_success(self, mock_db, mock_user):
        with (
            patch("services.auth.get_user_by_email", return_value=mock_user),
            patch("services.auth.verify_password", return_value=True),
            patch("services.auth.create_access_token", return_value="tok123"),
        ):
            result = authenticate_user(self._make_payload(), mock_db)

        assert result.access_token == "tok123"
        assert result.token_type == "bearer"
        assert result.user == mock_user
