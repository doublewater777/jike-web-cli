# cli-web-jike

[![PyPI version](https://img.shields.io/pypi/v/cli-web-jike)](https://pypi.org/project/cli-web-jike/)
[![Python](https://img.shields.io/pypi/pyversions/cli-web-jike)](https://pypi.org/project/cli-web-jike/)

CLI for [Jike (即刻)](https://web.okjike.com/) — browse feeds, create posts, upload images, search topics, all from your terminal.

## Features

- 🔐 **Auth** — browser-based SMS/WeChat login, JWT token auto-refresh, status check
- 📰 **Feed** — following feed, explore/discover feed
- ✍️ **Post** — create text posts, upload images, draft topic suggestions
- 👤 **Users** — profile, followers, following lists
- 🏷️ **Topics** — topic detail, topic feed
- 🔔 **Notifications** — list, unread count
- 🔍 **Search** — autocomplete suggestions (topics, users, keywords)
- 💬 **Comments** — view post comments
- 📊 **Structured output** — `--json` on every command for AI agents and scripting
- 🖥️ **REPL mode** — interactive shell with command history and auto-completion

## Installation

```bash
# Recommended: pipx
pipx install cli-web-jike

# Or: pip
pip install cli-web-jike
```

For browser-based auth:
```bash
pip install cli-web-jike[auth]
playwright install chromium
```

> **Tip:** Token expires periodically. Run `cli-web-jike auth login` to refresh via browser.

From source:
```bash
git clone git@github.com:doublewater777/cli-web-jike.git
cd cli-web-jike
pip install -e ".[auth]"
```

## Usage

```bash
# ─── Auth ─────────────────────────────────────────
cli-web-jike auth login                 # Browser-based SMS/WeChat login
cli-web-jike auth status                # Check login state
cli-web-jike auth status --json         # JSON output
cli-web-jike auth logout                # Remove saved credentials

# ─── Feed ─────────────────────────────────────────
cli-web-jike feed following             # Your following feed
cli-web-jike feed following --limit 10  # More posts
cli-web-jike feed explore               # Explore/discover feed
cli-web-jike feed explore --limit 20    # With pagination key
cli-web-jike --json feed following      # JSON for scripting

# ─── Posts ────────────────────────────────────────
cli-web-jike posts get <post_id>        # Read a post
cli-web-jike posts create "Hello Jike"  # Create a text post
cli-web-jike posts create "Check this" --image ~/photo.png  # Post with image
cli-web-jike posts create "AI stuff" --topic-id <topic_id>  # Post to a topic
cli-web-jike posts suggest "AI 相关"    # Get topic suggestions for a draft

# ─── Users ────────────────────────────────────────
cli-web-jike users profile              # Your own profile
cli-web-jike users profile <username>   # Another user's profile
cli-web-jike users following <username> # Who they follow
cli-web-jike users followers <username> # Who follows them

# ─── Topics ───────────────────────────────────────
cli-web-jike topics get <topic_id>      # Topic details
cli-web-jike topics feed <topic_id>     # Posts in a topic (圈子)

# ─── Notifications ────────────────────────────────
cli-web-jike notifications list         # Your notifications
cli-web-jike notifications unread       # Unread count

# ─── Search ───────────────────────────────────────
cli-web-jike search suggestions "AI"    # Autocomplete
cli-web-jike search suggestions "AI" --limit 10

# ─── Comments ─────────────────────────────────────
cli-web-jike comments list <post_id>    # Comments on a post
```

Run `cli-web-jike` without arguments for interactive REPL mode.

## Auth

JWT token stored at `~/.config/cli-web-jike/auth.json` (chmod 600).

For CI/CD, set:
```bash
export CLI_WEB_JIKE_AUTH_JSON='{"token": "eyJ..."}'
```

Token auto-refresh: on 401/403, the CLI retries up to 3 times (reload from disk → headless browser refresh → fail with guidance).

## Structured Output

All commands support `--json`:

```bash
cli-web-jike --json feed following --limit 3
```

Success:
```json
{"success": true, "data": [...]}
```

Error:
```json
{"error": true, "code": "AUTH_EXPIRED", "message": "Session expired. Run: cli-web-jike auth login"}
```

## Use as AI Agent Skill

cli-web-jike ships with a `SKILL.md` that teaches AI agents how to use it.

### Skills CLI (Recommended)

```bash
npx skills add doublewater777/cli-web-jike
```

### Manual Install

```bash
mkdir -p .claude/skills/jike-cli
cp SKILL.md .claude/skills/jike-cli/
```

## Project Structure

```
cli_web/jike/
├── jike_cli.py          # Click entry point & command registration
├── core/
│   ├── client.py        # httpx REST client (3-attempt JWT refresh)
│   ├── auth.py          # Playwright browser login + JWT token storage
│   └── exceptions.py    # Typed hierarchy (AuthError, NotFoundError, etc.)
├── commands/
│   ├── feed.py          # following, explore
│   ├── posts.py         # get, create, suggest
│   ├── users.py         # profile, following, followers
│   ├── topics.py        # get, feed
│   ├── notifications.py # list, unread
│   ├── search.py        # suggestions
│   └── comments.py      # list
├── utils/               # helpers, output, repl_skin
└── tests/               # unit + e2e + subprocess
```

## Troubleshooting

**Q: AuthError — Not logged in**

Run `cli-web-jike auth login` to open the browser and log in via SMS/WeChat.

**Q: AuthError — Session expired**

JWT tokens are short-lived. Run `cli-web-jike auth login` to refresh.

**Q: Login opens browser but token isn't saved**

After logging in, make sure the page redirects to your feed, then press Enter in the terminal. The CLI extracts the `JK_ACCESS_TOKEN` from localStorage.

## Links

- [PyPI](https://pypi.org/project/cli-web-jike/)
- [GitHub](https://github.com/doublewater777/cli-web-jike)
