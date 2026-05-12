"""Notification commands for jike."""

from __future__ import annotations

import click

from ..core.client import JikeClient
from ..utils.helpers import handle_errors, print_json


@click.group()
def notifications():
    """View notifications and unread count."""


@notifications.command("list")
@click.option("--limit", type=int, default=20, help="Number of notifications.")
@click.option("--load-more-key", default=None, help="Pagination key.")
@click.pass_context
def notifications_list(ctx, limit, load_more_key):
    """List your notifications."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.notifications_list(
            limit=min(limit, 50), load_more_key=load_more_key
        )
        items = data if isinstance(data, list) else data.get("data", [])
        if ctx.obj.get("json"):
            print_json(
                {
                    "success": True,
                    "data": items,
                    "loadMoreKey": data.get("loadMoreKey")
                    if isinstance(data, dict)
                    else None,
                }
            )
        else:
            for n in items:
                action = n.get("actionType", "?")
                ref = n.get("referenceItem", {}) or {}
                ref_text = ref.get("content", "") if isinstance(ref, dict) else str(ref)
                click.echo(f"[{action}] {ref_text[:100]}")
                click.echo(f"  {n.get('createdAt', '?')}  —  {n.get('id', '')}")
                click.echo()


@notifications.command("unread")
@click.pass_context
def notifications_unread(ctx):
    """Get unread notification count."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.unread_count()
        count = data.get("unreadCount", 0)
        if ctx.obj.get("json"):
            print_json({"success": True, "data": {"unreadCount": count}})
        else:
            click.echo(f"Unread notifications: {count}")
