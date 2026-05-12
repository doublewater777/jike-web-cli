"""Comment commands for cli-web-jike."""
from __future__ import annotations

import click

from ..core.client import JikeClient
from ..utils.helpers import handle_errors, print_json


@click.group()
def comments():
    """View comments on posts."""


@comments.command("list")
@click.argument("post_id")
@click.option("--limit", type=int, default=20, help="Number of comments.")
@click.option("--load-more-key", default=None, help="Pagination key.")
@click.pass_context
def comments_list(ctx, post_id, limit, load_more_key):
    """List primary comments on a post."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.get_comments(post_id, limit=min(limit, 50), load_more_key=load_more_key)
        items = data if isinstance(data, list) else data.get("data", [])
        if ctx.obj.get("json"):
            print_json({"success": True, "data": items, "loadMoreKey": data.get("loadMoreKey") if isinstance(data, dict) else None})
        else:
            for c in items:
                user = c.get("user", {})
                click.echo(f"[{user.get('screenName', '?')}] {c.get('content', '')[:120]}")
                click.echo(f"  ❤ {c.get('likeCount', 0)}  💬 {c.get('replyCount', 0)}  — {c.get('id', '')}")
                click.echo()
