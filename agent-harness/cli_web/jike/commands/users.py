"""User commands for jike."""

from __future__ import annotations

import click

from ..core.client import JikeClient
from ..utils.helpers import handle_errors, print_json


@click.group()
def users():
    """View user profiles and relations."""


@users.command("profile")
@click.argument("username", required=False, default=None)
@click.pass_context
def users_profile(ctx, username):
    """Get your own profile or another user's profile by username (UUID)."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.get_profile(username=username)
        if ctx.obj.get("json"):
            print_json({"success": True, "data": data})
        else:
            user_data = data.get("user", data) if isinstance(data, dict) else data
            if "user" in user_data:
                profile = user_data["user"]
            else:
                profile = user_data
            click.echo(f"Name: {profile.get('screenName', '?')}")
            click.echo(f"Username: {profile.get('username', '?')}")
            click.echo(
                f"Bio: {profile.get('briefIntro', '') or profile.get('bio', '')}"
            )
            stats = profile.get("statsCount", {})
            click.echo(
                f"Following: {stats.get('followingCount', 0)}  Followers: {stats.get('followedCount', 0)}"
            )


@users.command("following")
@click.argument("username")
@click.option("--limit", type=int, default=20, help="Number of users.")
@click.option("--load-more-key", default=None, help="Pagination key.")
@click.pass_context
def users_following(ctx, username, limit, load_more_key):
    """List users that a given user follows."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.get_following(
            username, limit=min(limit, 50), load_more_key=load_more_key
        )
        users_list = data if isinstance(data, list) else data.get("data", [])
        if ctx.obj.get("json"):
            print_json(
                {
                    "success": True,
                    "data": users_list,
                    "loadMoreKey": data.get("loadMoreKey")
                    if isinstance(data, dict)
                    else None,
                }
            )
        else:
            for u in users_list:
                click.echo(
                    f"{u.get('screenName', '?')} (@{u.get('username', '?')}) — {u.get('briefIntro', '')[:80]}"
                )


@users.command("followers")
@click.argument("username")
@click.option("--limit", type=int, default=20, help="Number of users.")
@click.option("--load-more-key", default=None, help="Pagination key.")
@click.pass_context
def users_followers(ctx, username, limit, load_more_key):
    """List followers of a given user."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.get_followers(
            username, limit=min(limit, 50), load_more_key=load_more_key
        )
        users_list = data if isinstance(data, list) else data.get("data", [])
        if ctx.obj.get("json"):
            print_json(
                {
                    "success": True,
                    "data": users_list,
                    "loadMoreKey": data.get("loadMoreKey")
                    if isinstance(data, dict)
                    else None,
                }
            )
        else:
            for u in users_list:
                click.echo(
                    f"{u.get('screenName', '?')} (@{u.get('username', '?')}) — {u.get('briefIntro', '')[:80]}"
                )
