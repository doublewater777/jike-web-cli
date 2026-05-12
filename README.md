# cli-web-jike

[![PyPI version](https://img.shields.io/pypi/v/cli-web-jike)](https://pypi.org/project/cli-web-jike/)
[![Python](https://img.shields.io/pypi/pyversions/cli-web-jike)](https://pypi.org/project/cli-web-jike/)

Agent-native CLI for [Jike (即刻)](https://web.okjike.com/) — browse feeds, create posts, upload images, search topics, all from your terminal.

## Install

```bash
pip install cli-web-jike
```

For browser-based auth (required for login):
```bash
pip install cli-web-jike[auth]
playwright install chromium
```

## Quick Start

```bash
# Login (opens browser for SMS/WeChat)
cli-web-jike auth login

# Your following feed
cli-web-jike feed following

# Create a post
cli-web-jike posts create "Hello Jike"

# Create a post with an image
cli-web-jike posts create "Check this out" --image ~/photo.png

# JSON output for scripting / AI agents
cli-web-jike --json feed following --limit 5
```

## Commands

| Group | Commands | Description |
|-------|----------|-------------|
| `auth` | `login`, `status`, `logout` | Browser-based SMS/WeChat login |
| `feed` | `following`, `explore` | Browse feeds |
| `posts` | `get`, `create`, `suggest` | Read and create posts (with image upload) |
| `users` | `profile`, `following`, `followers` | User profiles and social graph |
| `topics` | `get`, `feed` | Topic/圈子 info and posts |
| `notifications` | `list`, `unread` | Notification management |
| `search` | `suggestions` | Search autocomplete |
| `comments` | `list` | Post comments |

Run `cli-web-jike` without arguments for interactive REPL mode.

## Links

- [PyPI](https://pypi.org/project/cli-web-jike/)
- [GitHub](https://github.com/doublewater777/cli-web-jike)
