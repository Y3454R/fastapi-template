import pytest
from fastapi import HTTPException

from schemas.blog import PostCreate
from services.blog import create_post, delete_post, get_posts


class TestGetPosts:
    def test_returns_all_posts(self, mock_db, mock_post):
        mock_db.query.return_value.all.return_value = [mock_post]
        result = get_posts(mock_db)
        assert result == [mock_post]


class TestCreatePost:
    def _make_payload(self, **kwargs):
        defaults = dict(title="Hello", content="World", category_id=None)
        return PostCreate(**{**defaults, **kwargs})

    def test_creates_and_returns_post(self, mock_db):
        mock_db.refresh.side_effect = lambda p: None
        result = create_post(self._make_payload(), author_id=1, db=mock_db)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_sets_author_id_from_parameter(self, mock_db):
        mock_db.refresh.side_effect = lambda p: None
        create_post(self._make_payload(), author_id=42, db=mock_db)
        added_post = mock_db.add.call_args[0][0]
        assert added_post.author_id == 42


class TestDeletePost:
    def test_raises_404_when_post_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            delete_post(99, author_id=1, db=mock_db)
        assert exc_info.value.status_code == 404

    def test_raises_403_when_not_author(self, mock_db, mock_post):
        mock_post.author_id = 5  # different from the requesting user
        mock_db.query.return_value.filter.return_value.first.return_value = mock_post
        with pytest.raises(HTTPException) as exc_info:
            delete_post(1, author_id=1, db=mock_db)
        assert exc_info.value.status_code == 403

    def test_deletes_post_successfully(self, mock_db, mock_post):
        mock_post.author_id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_post
        delete_post(1, author_id=1, db=mock_db)
        mock_db.delete.assert_called_once_with(mock_post)
        mock_db.commit.assert_called_once()
