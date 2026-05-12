# jike-web-cli

[![PyPI version](https://img.shields.io/pypi/v/jike-web-cli)](https://pypi.org/project/jike-web-cli/)
[![Python](https://img.shields.io/pypi/pyversions/jike-web-cli)](https://pypi.org/project/jike-web-cli/)

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
pipx install jike-web-cli
pip install jike-web-cli
pip install jike-web-cli[auth]
playwright install chromium
```

> **Tip:** Token expires periodically. Run `jike auth login` to refresh via browser.

From source:
```bash
git clone git@github.com:doublewater777/jike-web-cli.git
cd jike-web-cli
pip install -e ".[auth]"
```

## Usage

```bash
# ─── Auth ─────────────────────────────────────────
jike auth login                 # Browser-based SMS/WeChat login
jike auth status                # Check login state
jike auth status --json         # JSON output
jike auth logout                # Remove saved credentials

# ─── Feed ─────────────────────────────────────────
jike feed following             # Your following feed
jike feed following --limit 10  # More posts
jike feed explore               # Explore/discover feed
jike feed explore --limit 20    # With pagination key
jike --json feed following      # JSON for scripting

# ─── Posts ────────────────────────────────────────
jike posts get <post_id>        # Read a post
jike posts create "Hello Jike"  # Create a text post
jike posts create "Check this" --image ~/photo.png  # Post with image
jike posts create "AI stuff" --topic-id <topic_id>  # Post to a topic
jike posts suggest "AI 相关"    # Get topic suggestions for a draft

# ─── Users ────────────────────────────────────────
jike users profile              # Your own profile
jike users profile <username>   # Another user's profile
jike users following <username> # Who they follow
jike users followers <username> # Who follows them

# ─── Topics ───────────────────────────────────────
jike topics get <topic_id>      # Topic details
jike topics feed <topic_id>     # Posts in a topic (圈子)

# ─── Notifications ────────────────────────────────
jike notifications list         # Your notifications
jike notifications unread       # Unread count

# ─── Search ───────────────────────────────────────
jike search suggestions "AI"    # Autocomplete
jike search suggestions "AI" --limit 10

# ─── Comments ─────────────────────────────────────
jike comments list <post_id>    # Comments on a post
```

Run `jike` without arguments for interactive REPL mode.

## Auth

JWT token stored at `~/.config/jike/auth.json` (chmod 600).

For CI/CD, set:
```bash
export JIKE_AUTH_JSON='{"token": "eyJ..."}'
```

Token auto-refresh: on 401/403, the CLI retries up to 3 times (reload from disk → headless browser refresh → fail with guidance).

## Structured Output

All commands support `--json`:

```bash
jike --json feed following --limit 3
```

Success:
```json
{"success": true, "data": [...]}
```

Error:
```json
{"error": true, "code": "AUTH_EXPIRED", "message": "Session expired. Run: jike auth login"}
```

## Use as AI Agent Skill

jike ships with a `SKILL.md` that teaches AI agents how to use it.

### Skills CLI (Recommended)

```bash
npx skills add doublewater777/jike-web-cli
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

Run `jike auth login` to open the browser and log in via SMS/WeChat.

**Q: AuthError — Session expired**

JWT tokens are short-lived. Run `jike auth login` to refresh.

**Q: Login opens browser but token isn't saved**

After logging in, make sure the page redirects to your feed, then press Enter in the terminal. The CLI extracts the `JK_ACCESS_TOKEN` from localStorage.

## Links

- [PyPI](https://pypi.org/project/jike-web-cli/)
- [GitHub](https://github.com/doublewater777/jike-web-cli)
