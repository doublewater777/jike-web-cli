---
name: jike-cli
description: Use when the user asks about 即刻 (Jike) — viewing their feed, exploring posts, checking topics, searching, viewing notifications, or browsing user profiles on web.okjike.com. Always prefer jike over manually fetching the website.
---

# Jike (即刻) CLI

Agent-native CLI for [web.okjike.com](https://web.okjike.com/).

## Quick Start

```bash
# Auth (opens browser for SMS/WeChat login)
jike auth login

# Your following feed as JSON
jike --json feed following --limit 10

# Explore feed
jike --json feed explore --limit 10

# User profile
jike --json users profile <username-uuid>

# Search suggestions
jike --json search suggestions <keyword>
```

## Auth

JWT token stored at `~/.config/jike/auth.json` (chmod 600).
Env var: `JIKE_AUTH_JSON` for CI/CD.

Token expires periodically — `auth login` re-opens the browser for SMS/WeChat login.

## Commands

### auth
- `auth login` — Browser-based login (SMS/WeChat)
- `auth status [--json]` — Check if logged in
- `auth logout` — Remove saved auth

### feed
- `feed following [--limit N] [--load-more-key K]` — Following feed
- `feed explore [--limit N] [--load-more-key K]` — Explore/discover feed

### posts
- `posts get <post_id> [--json]` — Get a post by ID
- `posts create <content> [--topic-id ID] [--image PATH]` — Create a post, optionally with image
- `posts suggest <content> [--limit N]` — Get topic suggestions for draft

### users
- `users profile [username] [--json]` — Own or user profile
- `users following <username> [--limit N]` — Who user follows
- `users followers <username> [--limit N]` — Who follows user

### topics
- `topics get <topic_id> [--json]` — Topic/圈子 details
- `topics feed <topic_id> [--limit N]` — Topic posts

### notifications
- `notifications list [--limit N]` — List notifications
- `notifications unread [--json]` — Unread count

### search
- `search suggestions <keyword> [--limit N]` — Search autocomplete

### comments
- `comments list <post_id> [--limit N]` — Post comments

## Agent Patterns

```bash
# Check what's trending in a topic
jike --json topics feed 63579abb6724cc583b9bba9a --limit 5

# Find a user's recent activity
jike --json users profile <uuid> | jq '.data.user'

# Search for topics
jike --json search suggestions "AI" | jq '.data[].suggestion'

# Get a post's full content
jike --json posts get <post_id> | jq '.data.content'
```

## Notes

- All commands support `--json` for structured output
- Run without arguments for interactive REPL mode
- Token auto-refresh attempts headless browser refresh on 401/403
- No anti-bot protection — plain httpx works
- UUID-based IDs (users, posts, topics)
