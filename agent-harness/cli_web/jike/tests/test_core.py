"""Unit tests for jike core modules (mocked HTTP)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from cli_web.jike.core.client import JikeClient
from cli_web.jike.core.exceptions import (
    AuthError,
    JikeError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    _error_code_for,
    raise_for_status,
)
from cli_web.jike.utils.helpers import handle_errors, print_json


# ── Exception hierarchy ──────────────────────────────────────────────────────────


class TestExceptions:
    def test_base_error_to_dict(self):
        exc = JikeError("something went wrong")
        d = exc.to_dict()
        assert d["error"] is True
        assert d["code"] == "UNKNOWN_ERROR"
        assert d["message"] == "something went wrong"

    def test_auth_error_code(self):
        exc = AuthError("expired", recoverable=True)
        assert _error_code_for(exc) == "AUTH_EXPIRED"
        assert exc.recoverable is True

    def test_rate_limit_error_with_retry_after(self):
        exc = RateLimitError("too fast", retry_after=60)
        d = exc.to_dict()
        assert d["code"] == "RATE_LIMITED"
        assert d["retry_after"] == 60

    def test_not_found_error_code(self):
        assert _error_code_for(NotFoundError("missing")) == "NOT_FOUND"

    def test_server_error_status_code(self):
        exc = ServerError("boom", status_code=502)
        assert exc.status_code == 502
        assert _error_code_for(exc) == "SERVER_ERROR"

    def test_network_error_code(self):
        assert _error_code_for(NetworkError("timeout")) == "NETWORK_ERROR"


class TestRaiseForStatus:
    def test_401_raises_auth_error(self):
        resp = MagicMock()
        resp.status_code = 401
        resp.text = "Unauthorized"
        with pytest.raises(AuthError) as exc_info:
            raise_for_status(resp)
        assert exc_info.value.recoverable is True

    def test_403_raises_auth_error(self):
        resp = MagicMock()
        resp.status_code = 403
        resp.text = "Forbidden"
        with pytest.raises(AuthError):
            raise_for_status(resp)

    def test_404_raises_not_found(self):
        resp = MagicMock()
        resp.status_code = 404
        resp.text = "Not Found"
        with pytest.raises(NotFoundError):
            raise_for_status(resp)

    def test_429_raises_rate_limit(self):
        resp = MagicMock()
        resp.status_code = 429
        resp.text = "Too Many Requests"
        resp.headers = {"Retry-After": "120"}
        with pytest.raises(RateLimitError) as exc_info:
            raise_for_status(resp)
        assert exc_info.value.retry_after == 120

    def test_500_raises_server_error(self):
        resp = MagicMock()
        resp.status_code = 500
        resp.text = "Internal Error"
        with pytest.raises(ServerError) as exc_info:
            raise_for_status(resp)
        assert exc_info.value.status_code == 500

    def test_200_does_not_raise(self):
        resp = MagicMock()
        resp.status_code = 200
        raise_for_status(resp)


# ── Client (mocked HTTP) ─────────────────────────────────────────────────────────


class TestClient:
    @pytest.fixture
    def mock_httpx(self):
        with patch("cli_web.jike.core.client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def client(self, mock_httpx):
        return JikeClient(token="test-token")

    def test_init_sets_headers(self):
        with patch("cli_web.jike.core.client.httpx.Client") as mock_client_class:
            JikeClient(token="my-token")
            call_args = mock_client_class.call_args
            headers = call_args[1]["headers"]
            assert headers["User-Agent"] == "jike/0.1.0"

    def test_request_injects_token_header(self, client, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {"data": "ok"}
        client.get_profile()
        _, kwargs = mock_httpx.request.call_args
        assert kwargs["headers"].get("x-jike-access-token") == "test-token"

    def test_401_triggers_token_reload(self, client, mock_httpx):
        mock_httpx.request.side_effect = [
            MagicMock(status_code=401, text="Unauthorized"),
            MagicMock(status_code=200, json=lambda: {"data": "ok"}),
        ]
        with patch.object(client, "_reload_token_from_disk") as mock_reload:
            client.get_profile()
            mock_reload.assert_called_once()

    def test_network_error_on_connect_failure(self, client, mock_httpx):
        import httpx

        mock_httpx.request.side_effect = httpx.ConnectError("connection refused")
        with pytest.raises(NetworkError, match="Connection failed"):
            client.get_profile()

    def test_get_profile(self, client, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {
            "user": {"screenName": "test"}
        }
        result = client.get_profile()
        assert "user" in result
        mock_httpx.request.assert_called_with(
            "GET",
            "https://api.ruguoapp.com/1.0/users/profile",
            headers=mock_httpx.request.call_args[1]["headers"],
            params={},
        )

    def test_get_profile_with_username(self, client, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {
            "user": {"screenName": "other"}
        }
        client.get_profile(username="some-uuid")
        mock_httpx.request.assert_called_with(
            "GET",
            "https://api.ruguoapp.com/1.0/users/profile",
            headers=mock_httpx.request.call_args[1]["headers"],
            params={"username": "some-uuid"},
        )

    def test_get_post(self, client, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {
            "data": {"id": "post-1", "content": "hello"}
        }
        result = client.get_post("post-1")
        assert result["id"] == "post-1"
        mock_httpx.request.assert_called_with(
            "GET",
            "https://api.ruguoapp.com/1.0/originalPosts/get",
            headers=mock_httpx.request.call_args[1]["headers"],
            params={"id": "post-1"},
        )

    def test_following_feed(self, client, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {
            "success": True,
            "data": [],
        }
        result = client.following_feed(limit=10)
        assert result == []
        method, path, kwargs = (
            mock_httpx.request.call_args[0],
            mock_httpx.request.call_args[1]["params"]
            if "params" in mock_httpx.request.call_args[1]
            else None,
            mock_httpx.request.call_args[1],
        )
        assert mock_httpx.request.call_args[1].get("json") == {"limit": 10}

    def test_following_feed_with_pagination(self, client, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {
            "success": True,
            "data": [],
        }
        client.following_feed(limit=10, load_more_key="key123")
        assert mock_httpx.request.call_args[1]["json"] == {
            "limit": 10,
            "loadMoreKey": "key123",
        }

    def test_explore_feed(self, client, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {"data": []}
        result = client.explore_feed()
        assert result == []

    def test_search_suggestions(self, client, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {
            "data": [{"suggestion": "AI"}]
        }
        result = client.search_suggestions("AI")
        assert result[0]["suggestion"] == "AI"

    def test_unread_count(self, client, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {"unreadCount": 5}
        result = client.unread_count()
        assert result["unreadCount"] == 5

    def test_close(self, client, mock_httpx):
        client.close()
        mock_httpx.close.assert_called_once()

    def test_context_manager(self, mock_httpx):
        mock_httpx.request.return_value.status_code = 200
        mock_httpx.request.return_value.json.return_value = {"data": "ok"}
        with JikeClient(token="ctx-token") as c:
            c.get_profile()
        mock_httpx.close.assert_called_once()


# ── Helpers ──────────────────────────────────────────────────────────────────────


class TestHandleErrors:
    def test_passes_through_success(self):
        with handle_errors(json_mode=False):
            pass

    def test_auth_error_exits_1(self):
        with pytest.raises(SystemExit) as exc_info:
            with handle_errors(json_mode=False):
                raise AuthError("expired")
        assert exc_info.value.code == 1

    def test_unknown_error_exits_2(self):
        with pytest.raises(SystemExit) as exc_info:
            with handle_errors(json_mode=False):
                raise ValueError("unexpected")
        assert exc_info.value.code == 2

    def test_keyboard_interrupt_exits_130(self):
        with pytest.raises(SystemExit) as exc_info:
            with handle_errors(json_mode=False):
                raise KeyboardInterrupt()
        assert exc_info.value.code == 130


class TestPrintJson:
    def test_prints_json_to_stdout(self, capsys):
        print_json({"success": True, "data": [1, 2, 3]})
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["success"] is True
        assert parsed["data"] == [1, 2, 3]
