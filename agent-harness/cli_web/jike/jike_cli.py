"""jike — CLI entry point."""

from __future__ import annotations

import sys

for _stream in (sys.stdout, sys.stderr):
    if _stream.encoding and _stream.encoding.lower() not in ("utf-8", "utf8"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass

import shlex

import click

from .core.auth import clear_auth, is_logged_in, login_browser
from .utils.helpers import handle_errors, print_json
from .utils.repl_skin import ReplSkin

_skin = ReplSkin(app="jike", version="0.1.0")


# ── Auth commands ────────────────────────────────────────────────────────────────


@click.group()
def auth():
    """Manage authentication."""


@auth.command("login")
def auth_login():
    """Log in via browser and save JWT access token."""
    try:
        data = login_browser()
        if data.get("token"):
            click.echo("Login successful — JWT token saved.")
        elif data.get("cookies"):
            click.echo("Login successful — session cookies saved.")
    except Exception as exc:
        click.secho(f"Login failed: {exc}", fg="red", err=True)
        raise SystemExit(1)


@auth.command("status")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON.")
def auth_status(json_mode):
    """Check authentication status."""
    with handle_errors(json_mode):
        logged_in = is_logged_in()
        if json_mode:
            print_json({"success": True, "data": {"logged_in": logged_in}})
        else:
            if logged_in:
                click.echo("Logged in ✓")
            else:
                click.echo("Not logged in. Run: jike auth login")


@auth.command("logout")
def auth_logout():
    """Remove saved authentication."""
    clear_auth()
    click.echo("Logged out — auth file removed.")


# ── Import command groups ────────────────────────────────────────────────────────

from .commands.feed import feed
from .commands.posts import posts
from .commands.users import users
from .commands.topics import topics
from .commands.notifications import notifications
from .commands.search import search
from .commands.comments import comments


# ── Main CLI group ────────────────────────────────────────────────────────────────


@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON.")
@click.version_option("0.1.0", prog_name="jike")
@click.pass_context
def cli(ctx, json_mode):
    """jike — CLI for Jike (即刻).

    Run without arguments to enter interactive REPL mode.
    """
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_mode

    if ctx.invoked_subcommand is None:
        _run_repl(ctx)


# ── Register commands ────────────────────────────────────────────────────────────

cli.add_command(auth)
cli.add_command(feed)
cli.add_command(posts)
cli.add_command(users)
cli.add_command(topics)
cli.add_command(notifications)
cli.add_command(search)
cli.add_command(comments)


# ── REPL ─────────────────────────────────────────────────────────────────────────


def _print_repl_help() -> None:
    _skin.info("Available commands:")
    print()
    print("  auth login                                  Log in via browser")
    print("  auth status [--json]                        Check auth status")
    print("  auth logout                                 Remove saved auth")
    print()
    print("  feed following [--limit N] [--load-more-key K]   Your following feed")
    print("  feed explore [--limit N] [--load-more-key K]     Explore/discover feed")
    print()
    print("  posts get <post_id> [--json]                     Get a post by ID")
    print()
    print("  users profile [username] [--json]                Get own/user profile")
    print("  users following <username> [--limit N]           List who user follows")
    print("  users followers <username> [--limit N]           List user's followers")
    print()
    print("  topics get <topic_id> [--json]                   Get topic details")
    print("  topics feed <topic_id> [--limit N]               Get topic posts")
    print()
    print("  notifications list [--limit N]                   List notifications")
    print("  notifications unread [--json]                    Unread count")
    print()
    print("  search suggestions <keyword> [--limit N]         Search suggestions")
    print()
    print("  comments list <post_id> [--limit N]              List post comments")
    print()
    print("  help                                            Show this help")
    print("  exit / quit / Ctrl-D                            Exit REPL")
    print()


def _run_repl(ctx: click.Context) -> None:
    _skin.print_banner()
    _print_repl_help()

    pt_session = _skin.create_prompt_session()

    while True:
        try:
            line = _skin.get_input(pt_session)
        except (EOFError, KeyboardInterrupt):
            _skin.print_goodbye()
            break

        line = line.strip()
        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            _skin.print_goodbye()
            break
        if line.lower() in ("help", "?", "h"):
            _print_repl_help()
            continue

        try:
            args = shlex.split(line)
        except ValueError as exc:
            _skin.error(f"Parse error: {exc}")
            continue

        if ctx.obj.get("json"):
            args = ["--json"] + args

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as exc:
            _skin.error(str(exc))


def main():
    cli()


if __name__ == "__main__":
    main()
