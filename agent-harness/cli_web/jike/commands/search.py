"""Search commands for jike."""

from __future__ import annotations

import click

from ..core.client import JikeClient
from ..utils.helpers import handle_errors, print_json


@click.group()
def search():
    """Search for topics, users, and posts."""


@search.command("suggestions")
@click.argument("keyword")
@click.option("--limit", type=int, default=10, help="Max suggestions.")
@click.pass_context
def search_suggestions(ctx, keyword, limit):
    """Get search suggestions for a keyword."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.search_suggestions(keyword, limit=min(limit, 50))
        items = data if isinstance(data, list) else data.get("data", [])
        if ctx.obj.get("json"):
            print_json({"success": True, "data": items})
        else:
            for item in items:
                item_type = item.get("type", "?")
                suggestion = item.get("suggestion", "?")
                click.echo(f"[{item_type}] {suggestion}")
                desc = item.get("description", "")
                if desc:
                    click.echo(f"  {desc[:100]}")
