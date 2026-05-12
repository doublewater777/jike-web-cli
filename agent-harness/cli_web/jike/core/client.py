"""HTTP client for jike."""

from __future__ import annotations

import json

import httpx

from .auth import get_token, load_auth, refresh_auth
from .exceptions import (
    AuthError,
    JikeError,
    NetworkError,
    raise_for_status,
)

API_BASE = "https://api.ruguoapp.com"


class JikeClient:
    """REST client with JWT auth and 3-attempt retry on 401/403."""

    def __init__(self, token: str | None = None):
        if token is None:
            try:
                token = get_token()
            except AuthError:
                token = None
        self._token = token
        self._client = httpx.Client(
            timeout=httpx.Timeout(connect=10.0, read=30.0, write=60.0, pool=30.0),
            headers={
                "User-Agent": "jike/0.1.0",
                "Accept": "application/json",
            },
        )

    def _headers(self) -> dict:
        h = {}
        if self._token:
            h["x-jike-access-token"] = self._token
        return h

    def _request(
        self,
        method: str,
        path: str,
        *,
        _attempt: int = 0,
        _base_override: str | None = None,
        _raw_response: bool = False,
        **kwargs,
    ) -> httpx.Response:
        kwargs.setdefault("headers", {}).update(self._headers())
        base = _base_override or API_BASE
        try:
            resp = self._client.request(method, f"{base}{path}", **kwargs)
        except httpx.ConnectError as exc:
            raise NetworkError(f"Connection failed: {exc}")
        except httpx.TimeoutException as exc:
            raise NetworkError(f"Request timed out: {exc}")

        if not _raw_response and resp.status_code in (401, 403) and _attempt < 2:
            if _attempt == 0:
                self._reload_token_from_disk()
            elif _attempt == 1:
                self._refresh_via_browser()
            return self._request(
                method,
                path,
                _attempt=_attempt + 1,
                _base_override=_base_override,
                _raw_response=_raw_response,
                **kwargs,
            )

        if not _raw_response:
            raise_for_status(resp)
        return resp

    def _parse(self, resp: httpx.Response) -> dict:
        """Parse JSON response, returning data dict."""
        body = resp.json()
        if "success" in body and not body["success"]:
            raise JikeError(body.get("message", "API returned failure"))
        return body.get("data", body)

    def _reload_token_from_disk(self) -> None:
        try:
            auth = load_auth()
            self._token = auth.get("token")
        except AuthError:
            pass

    def _refresh_via_browser(self) -> None:
        auth = refresh_auth()
        if auth and auth.get("token"):
            self._token = auth["token"]
        else:
            raise AuthError(
                "Session expired and auto-refresh failed. Run: jike auth login",
                recoverable=False,
            )

    # --- Feed ---

    def following_feed(self, limit: int = 20, load_more_key: str | None = None) -> dict:
        body = {"limit": limit}
        if load_more_key:
            body["loadMoreKey"] = load_more_key
        resp = self._request("POST", "/1.0/personalUpdate/followingUpdates", json=body)
        return self._parse(resp)

    def explore_feed(self, limit: int = 20, load_more_key: str | None = None) -> dict:
        body = {"limit": limit}
        if load_more_key:
            body["loadMoreKey"] = load_more_key
        resp = self._request("POST", "/1.0/recommendFeed/list", json=body)
        return self._parse(resp)

    # --- Posts ---

    def get_post(self, post_id: str) -> dict:
        resp = self._request("GET", "/1.0/originalPosts/get", params={"id": post_id})
        return self._parse(resp)

    def create_post(
        self,
        content: str,
        picture_keys: list | None = None,
        topic_id: str | None = None,
    ) -> dict:
        body = {
            "content": content,
            "pictureKeys": picture_keys or [],
            "syncToPersonalUpdate": True,
        }
        if topic_id:
            body["submitToTopic"] = topic_id
        resp = self._request("POST", "/1.0/originalPosts/create", json=body)
        return self._parse(resp)

    def draft_suggestions(self, content: str, limit: int = 5) -> dict:
        body = {
            "content": content,
            "localTimezone": "Asia/Shanghai",
            "pictures": [],
            "limit": limit,
        }
        resp = self._request(
            "POST", "/1.0/originalPosts/listDraftSuggestions", json=body
        )
        return self._parse(resp)

    # --- Image upload ---

    def get_upload_token(self) -> dict:
        resp = self._request(
            "GET",
            "/token",
            params={"bucket": "jike", "uploadType": "PIC"},
            _base_override="https://upload.ruguoapp.com",
        )
        return resp.json()

    def upload_image(self, file_path: str) -> str:
        """Upload an image and return its picture key.

        1. Gets an upload token from Jike
        2. Uploads the file to Qiniu Cloud
        3. Returns the picture key for use in create_post()
        """
        import mimetypes
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        # Step 1: Get upload token
        token_data = self.get_upload_token()
        uptoken = token_data.get("uptoken", "")

        # Step 2: Upload to Qiniu
        mime_type = mimetypes.guess_type(file_path)[0] or "image/png"
        with open(file_path, "rb") as f:
            files = {"file": (path.name, f, mime_type)}
            data = {"token": uptoken}
            resp = self._request(
                "POST",
                "/",
                data=data,
                files=files,
                _base_override="https://upload.qiniup.com",
                _raw_response=True,
            )

        result = resp.json()
        if not result.get("success"):
            raise RuntimeError(f"Image upload failed: {result}")

        return result["key"]

    # --- Users ---

    def get_profile(self, username: str | None = None) -> dict:
        params = {}
        if username:
            params["username"] = username
        resp = self._request("GET", "/1.0/users/profile", params=params)
        return self._parse(resp)

    def get_following(
        self, username: str, limit: int = 20, load_more_key: str | None = None
    ) -> dict:
        body = {"username": username, "limit": limit}
        if load_more_key:
            body["loadMoreKey"] = load_more_key
        resp = self._request("POST", "/1.0/userRelation/getFollowingList", json=body)
        return self._parse(resp)

    def get_followers(
        self, username: str, limit: int = 20, load_more_key: str | None = None
    ) -> dict:
        body = {"username": username, "limit": limit}
        if load_more_key:
            body["loadMoreKey"] = load_more_key
        resp = self._request("POST", "/1.0/userRelation/getFollowerList", json=body)
        return self._parse(resp)

    # --- Topics ---

    def get_topic(self, topic_id: str) -> dict:
        resp = self._request("GET", "/1.0/topics/getDetail", params={"id": topic_id})
        return self._parse(resp)

    def topic_feed(
        self, topic_id: str, limit: int = 20, load_more_key: str | None = None
    ) -> dict:
        body = {"topicId": topic_id, "limit": limit}
        if load_more_key:
            body["loadMoreKey"] = load_more_key
        resp = self._request("POST", "/1.0/topics/tabs/square/feed", json=body)
        return resp.json()

    # --- Notifications ---

    def notifications_list(
        self, limit: int = 20, load_more_key: str | None = None
    ) -> dict:
        body = {"limit": limit}
        if load_more_key:
            body["loadMoreKey"] = load_more_key
        resp = self._request("POST", "/1.0/notifications/list", json=body)
        return resp.json()

    def unread_count(self) -> dict:
        resp = self._request("GET", "/1.0/notifications/unread")
        return resp.json()

    # --- Search ---

    def search_suggestions(self, keyword: str, limit: int = 10) -> dict:
        resp = self._request(
            "GET",
            "/1.0/related/keywordTip",
            params={"keyword": keyword, "limit": limit},
        )
        return self._parse(resp)

    # --- Comments ---

    def get_comments(
        self, target_id: str, limit: int = 20, load_more_key: str | None = None
    ) -> dict:
        body = {"targetId": target_id, "limit": limit}
        if load_more_key:
            body["loadMoreKey"] = load_more_key
        resp = self._request("POST", "/1.0/comments/listPrimary", json=body)
        return resp.json()

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
