"""Topic commands for cli-web-jike."""
from __future__ import annotations

import click

from ..core.client import JikeClient
from ..utils.helpers import handle_errors, print_json


@click.group()
def topics():
    """Browse topics (圈子) and their posts."""


@topics.command("get")
@click.argument("topic_id")
@click.pass_context
def topics_get(ctx, topic_id):
    """Get topic details by ID."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.get_topic(topic_id)
        if ctx.obj.get("json"):
            print_json({"success": True, "data": data})
        else:
            click.echo(f"Topic: {data.get('content', '?')}")
            click.echo(f"ID: {data.get('id', data.get('topicId', '?'))}")
            click.echo(f"Subscribers: {data.get('subscribersCount', 0)}")
            click.echo(f"Intro: {data.get('intro', '') or data.get('briefIntro', '')}")


@topics.command("feed")
@click.argument("topic_id")
@click.option("--limit", type=int, default=20, help="Number of posts.")
@click.option("--load-more-key", default=None, help="Pagination key.")
@click.pass_context
def topics_feed(ctx, topic_id, limit, load_more_key):
    """Get posts from a topic."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.topic_feed(topic_id, limit=min(limit, 50), load_more_key=load_more_key)
        posts = data if isinstance(data, list) else data.get("data", [])
        if ctx.obj.get("json"):
            print_json({"success": True, "data": posts, "loadMoreKey": data.get("loadMoreKey") if isinstance(data, dict) else None})
        else:
            for post in posts:
                user = post.get("user", {})
                click.echo(f"[{user.get('screenName', '?')}] {post.get('content', '')[:120]}")
                click.echo(f"  ❤ {post.get('likeCount', 0)}  💬 {post.get('commentCount', 0)}  — {post.get('id', '')}")
                click.echo()
