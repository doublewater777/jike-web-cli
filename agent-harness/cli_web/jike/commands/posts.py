"""Post commands for cli-web-jike."""
from __future__ import annotations

import click

from ..core.client import JikeClient
from ..utils.helpers import handle_errors, print_json


@click.group()
def posts():
    """Get, create, and inspect posts."""


@posts.command("get")
@click.argument("post_id")
@click.pass_context
def posts_get(ctx, post_id):
    """Get a single post by ID."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.get_post(post_id)
        if ctx.obj.get("json"):
            print_json({"success": True, "data": data})
        else:
            post = data if isinstance(data, dict) else (data.get("data", {}) if isinstance(data, dict) else {})
            user = post.get("user", {})
            click.echo(f"Post: {post.get('id', '?')}")
            click.echo(f"By: {user.get('screenName', '?')} (@{user.get('username', '?')})")
            click.echo(f"At: {post.get('createdAt', '?')}")
            click.echo()
            click.echo(post.get("content", ""))
            click.echo()
            click.echo(f"❤ {post.get('likeCount', 0)}  💬 {post.get('commentCount', 0)}  🔄 {post.get('repostCount', 0)}")
            if post.get("topic"):
                click.echo(f"Topic: {post['topic'].get('content', '')}")


@posts.command("create")
@click.argument("content")
@click.option("--topic-id", default=None, help="Topic/圈子 ID to post to.")
@click.option("--image", "image_path", default=None, help="Path to an image file to attach.")
@click.pass_context
def posts_create(ctx, content, topic_id, image_path):
    """Create a new post (动态). Optionally attach an image."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        picture_keys = []
        if image_path:
            key = client.upload_image(image_path)
            picture_keys = [key]
            if not ctx.obj.get("json"):
                click.echo(f"Image uploaded: {key}")
        data = client.create_post(content, picture_keys=picture_keys, topic_id=topic_id)
        if ctx.obj.get("json"):
            print_json({"success": True, "data": data})
        else:
            post = data if isinstance(data, dict) else {}
            click.echo(f"Post created: {post.get('id', '?')}")
            click.echo(f"Content: {post.get('content', content)[:100]}")


@posts.command("suggest")
@click.argument("content")
@click.option("--limit", type=int, default=5, help="Number of suggestions.")
@click.pass_context
def posts_suggest(ctx, content, limit):
    """Get topic suggestions for a draft post."""
    with handle_errors(ctx.obj.get("json")):
        client = JikeClient()
        data = client.draft_suggestions(content, limit=limit)
        items = data if isinstance(data, list) else data.get("data", [])
        if ctx.obj.get("json"):
            print_json({"success": True, "data": items})
        else:
            for item in items:
                click.echo(f"[{item.get('type', '?')}] {item.get('content', item.get('suggestion', '?'))}")
