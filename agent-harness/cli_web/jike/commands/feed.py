"""Feed commands for jike."""

from __future__ import annotations

import click

from ..core.client import JikeClient
from ..utils.helpers import handle_errors, print_json
from ..utils.output import json_success


@click.group()
def feed():
    """Browse your following and explore feeds."""


@feed.command("following")
@click.option("--limit", type=int, default=20, help="Number of posts (max 50).")
@click.option("--load-more-key", default=None, help="Pagination key for next page.")
@click.pass_context
def feed_following(ctx, limit, load_more_key):
    """Get your following feed."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.following_feed(limit=min(limit, 50), load_more_key=load_more_key)
        posts = data if isinstance(data, list) else data.get("data", [])
        if ctx.obj.get("json"):
            print_json(
                {
                    "success": True,
                    "data": posts,
                    "loadMoreKey": data.get("loadMoreKey")
                    if isinstance(data, dict)
                    else None,
                }
            )
        else:
            for post in posts:
                user = post.get("user", {})
                click.echo(
                    f"[{user.get('screenName', '?')}] {post.get('content', '')[:120]}"
                )
                click.echo(
                    f"  ❤ {post.get('likeCount', 0)}  💬 {post.get('commentCount', 0)}  🔄 {post.get('repostCount', 0)}  — {post.get('id', '')}"
                )
                click.echo()


@feed.command("explore")
@click.option("--limit", type=int, default=20, help="Number of posts (max 50).")
@click.option("--load-more-key", default=None, help="Pagination key for next page.")
@click.pass_context
def feed_explore(ctx, limit, load_more_key):
    """Get the explore/discover feed."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.explore_feed(limit=min(limit, 50), load_more_key=load_more_key)
        posts = data if isinstance(data, list) else data.get("data", [])
        if ctx.obj.get("json"):
            print_json(
                {
                    "success": True,
                    "data": posts,
                    "loadMoreKey": data.get("loadMoreKey")
                    if isinstance(data, dict)
                    else None,
                }
            )
        else:
            for post in posts:
                user = post.get("user", {})
                topic = post.get("topic", {})
                topic_str = f"  #{topic.get('content', '')}" if topic else ""
                click.echo(
                    f"[{user.get('screenName', '?')}] {post.get('content', '')[:120]}"
                )
                if topic_str:
                    click.echo(topic_str)
                click.echo(
                    f"  ❤ {post.get('likeCount', 0)}  💬 {post.get('commentCount', 0)}  — {post.get('id', '')}"
                )
                click.echo()
