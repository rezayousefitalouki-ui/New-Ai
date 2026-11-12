from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.content.meta_publishing import PublishingError, publish_target
from apps.content.models import Post, PostTarget


@shared_task
def enqueue_due_posts():
    due_ids = list(
        Post.objects.filter(
            status=Post.Status.SCHEDULED,
            scheduled_at__lte=timezone.now(),
        ).values_list("id", flat=True)[:100]
    )
    for post_id in due_ids:
        with transaction.atomic():
            post = Post.objects.select_for_update().filter(
                id=post_id,
                status=Post.Status.SCHEDULED,
            ).first()
            if not post:
                continue
            post.status = Post.Status.PUBLISHING
            post.save(update_fields=("status", "updated_at"))
        publish_post.delay(str(post_id))


@shared_task
def publish_post(post_id):
    post = Post.objects.filter(id=post_id).first()
    if not post or post.status not in (Post.Status.PUBLISHING, Post.Status.SCHEDULED):
        return
    failed = False
    published_any = False
    targets = post.targets.select_related("social_account").filter(
        status__in=(PostTarget.Status.QUEUED, PostTarget.Status.FAILED)
    )
    for target in targets:
        target.status = PostTarget.Status.PUBLISHING
        target.attempts += 1
        target.error_message = ""
        target.save(update_fields=("status", "attempts", "error_message"))
        try:
            remote_id = publish_target(target)
        except (PublishingError, ValueError) as exc:
            target.status = PostTarget.Status.FAILED
            target.error_message = str(exc)[:300]
            target.save(update_fields=("status", "error_message"))
            failed = True
        else:
            target.status = PostTarget.Status.PUBLISHED
            target.remote_id = remote_id
            target.published_at = timezone.now()
            target.save(update_fields=("status", "remote_id", "published_at"))
            published_any = True
    post.refresh_from_db()
    remaining = post.targets.exclude(status=PostTarget.Status.PUBLISHED).exists()
    if failed or remaining:
        post.status = Post.Status.FAILED
    else:
        post.status = Post.Status.PUBLISHED
        post.published_at = timezone.now() if published_any else None
    post.save(update_fields=("status", "published_at", "updated_at"))
