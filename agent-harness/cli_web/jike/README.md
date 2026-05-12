# cli-web-jike

CLI for [Jike (即刻)](https://web.okjike.com/) — a Chinese social networking platform.

## Installation

```bash
pip install -e jike/agent-harness
```

For browser-based authentication:
```bash
pip install -e "jike/agent-harness[auth]"
playwright install chromium
```

## Quick Start

```bash
# Authenticate (opens browser for SMS/WeChat login)
cli-web-jike auth login

# Your following feed
cli-web-jike feed following

# Create a post
cli-web-jike posts create "Hello Jike"

# Create a post with an image
cli-web-jike posts create "Check this out" --image ~/photo.png

# All commands support --json output
cli-web-jike --json feed following --limit 5
```

## Commands

### auth
| Command | Description |
|---------|-------------|
| `auth login` | Open browser for SMS/WeChat login |
| `auth status [--json]` | Check authentication state |
| `auth logout` | Remove saved credentials |

### feed
| Command | Description |
|---------|-------------|
| `feed following [--limit N] [--load-more-key K]` | Your following feed |
| `feed explore [--limit N] [--load-more-key K]` | Explore/discover feed |

### posts
| Command | Description |
|---------|-------------|
| `posts get <id>` | Get a post by ID |
| `posts create <content> [--topic-id ID] [--image PATH]` | Create a post, optionally with an image |
| `posts suggest <draft>` | Get topic suggestions for a draft |

### users
| Command | Description |
|---------|-------------|
| `users profile [username]` | Get your own or another user's profile |
| `users following <username> [--limit N]` | List who a user follows |
| `users followers <username> [--limit N]` | List a user's followers |

### topics
| Command | Description |
|---------|-------------|
| `topics get <id>` | Get topic/圈子 details |
| `topics feed <id> [--limit N]` | Get posts from a topic |

### notifications
| Command | Description |
|---------|-------------|
| `notifications list [--limit N]` | List notifications |
| `notifications unread` | Unread notification count |

### search
| Command | Description |
|---------|-------------|
| `search suggestions <keyword> [--limit N]` | Search autocomplete (topics, users, keywords) |

### comments
| Command | Description |
|---------|-------------|
| `comments list <post_id> [--limit N]` | List primary comments on a post |

## Auth

JWT token stored at `~/.config/cli-web-jike/auth.json` (chmod 600).
For CI/CD, set the `CLI_WEB_JIKE_AUTH_JSON` environment variable with a JSON `{"token": "..."}` value.

Token expiration: tokens are short-lived. Run `auth login` to refresh via browser.

## REPL Mode

Run `cli-web-jike` without arguments to enter interactive REPL mode with:
- Command history
- Auto-completion
- Branded banner

```bash
cli-web-jike
> feed following --limit 3
> users profile
> exit
```
