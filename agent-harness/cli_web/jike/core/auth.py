"""Auth management for jike.

Uses Python playwright for browser-based login.
Stores JWT access token at ~/.config/jike/auth.json.
"""

from __future__ import annotations

import asyncio
import json
import os
import platform
import stat
import sys
from pathlib import Path

from .exceptions import AuthError

CONFIG_DIR = Path.home() / ".config" / "jike"
AUTH_FILE = CONFIG_DIR / "auth.json"
ENV_VAR = "JIKE_AUTH_JSON"
PROFILE_DIR = CONFIG_DIR / "browser-profile"

SITE_URL = "https://web.okjike.com"
LOGIN_URL = "https://web.okjike.com/login"


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def save_auth(data: dict) -> Path:
    _ensure_dir()
    AUTH_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    if platform.system() != "Windows":
        AUTH_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)
    else:
        try:
            os.chmod(AUTH_FILE, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass
    return AUTH_FILE


def load_auth() -> dict:
    """Load auth from env var or file. Returns dict with 'token' key.

    Raises AuthError if no auth data found.
    """
    env_val = os.environ.get(ENV_VAR)
    if env_val:
        try:
            data = json.loads(env_val)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    if AUTH_FILE.exists():
        try:
            data = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
            # Handle playwright storage state (array of cookie objects)
            if isinstance(data, dict) and "token" in data:
                return data
            if isinstance(data, dict) and "cookies" in data:
                return data
            if isinstance(data, list):
                return {"cookies": data}
            if isinstance(data, dict):
                return {"token": data.get("token"), "cookies": data.get("cookies")}
        except (json.JSONDecodeError, OSError):
            pass

    raise AuthError("Not logged in. Run: jike auth login")


def get_token() -> str:
    """Get the JWT access token for API requests.

    Raises AuthError if not logged in.
    """
    auth = load_auth()
    token = auth.get("token")
    if token:
        return token
    raise AuthError("No access token. Run: jike auth login")


def clear_auth() -> None:
    if AUTH_FILE.exists():
        AUTH_FILE.unlink()


def is_logged_in() -> bool:
    try:
        load_auth()
        return True
    except AuthError:
        return False


# ---------------------------------------------------------------------------
# Token refresh (headless browser)
# ---------------------------------------------------------------------------


def refresh_auth() -> dict | None:
    """Silently refresh the JWT token using the persistent browser profile."""
    if not PROFILE_DIR.exists():
        return None

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(SITE_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            token = page.evaluate(
                "() => localStorage.getItem('JK_ACCESS_TOKEN') || localStorage.getItem('accessToken') || localStorage.getItem('token') || ''"
            )
            context.close()

        if token:
            auth_data = {"token": token}
            save_auth(auth_data)
            return auth_data
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Browser login
# ---------------------------------------------------------------------------


def login_browser() -> dict:
    """Open browser for manual login, extract JWT access token.

    Returns dict with 'token' key.
    """
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.goto(LOGIN_URL)

        print("\n  Please log in in the browser window (SMS / WeChat).")
        print("  After login, the page should redirect to your feed.")
        print("  Press Enter here when you're logged in.\n")
        input("  Waiting... ")

        page.goto(SITE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Clear any stale token so SPA refreshes from session cookies
        page.evaluate("() => localStorage.removeItem('JK_ACCESS_TOKEN')")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Extract JWT token from localStorage
        token = page.evaluate(
            "() => localStorage.getItem('JK_ACCESS_TOKEN') "
            "|| localStorage.getItem('accessToken') "
            "|| localStorage.getItem('token') "
            "|| ''"
        )

        # Also capture cookies as fallback
        cookies = context.cookies()
        cookie_dict = {}
        for c in cookies:
            if "okjike.com" in c.get("domain", "") or "ruguoapp.com" in c.get(
                "domain", ""
            ):
                cookie_dict[c["name"]] = c["value"]

        context.close()

    if not token and not cookie_dict:
        raise AuthError("Login failed — no token or session cookies found.")

    auth_data = {}
    if token:
        auth_data["token"] = token
    if cookie_dict:
        auth_data["cookies"] = cookie_dict

    save_auth(auth_data)
    return auth_data
