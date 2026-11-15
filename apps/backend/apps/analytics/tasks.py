from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.analytics.services import AnalyticsError, sync_instagram_account
from apps.social_accounts.models import SocialAccount


@shared_task
def sync_analytics_account(account_id):
    account = SocialAccount.objects.filter(
        id=account_id,
        platform=SocialAccount.Platform.INSTAGRAM,
        status=SocialAccount.Status.CONNECTED,
    ).first()
    if not account:
        return
    try:
        sync_instagram_account(account)
    except AnalyticsError as exc:
        SocialAccount.objects.filter(id=account.id).update(last_error=str(exc)[:250])
    else:
        SocialAccount.objects.filter(id=account.id).update(last_error="")


@shared_task
def enqueue_analytics_syncs():
    cutoff = timezone.now() - timedelta(hours=6)
    accounts = SocialAccount.objects.filter(
        platform=SocialAccount.Platform.INSTAGRAM,
        status=SocialAccount.Status.CONNECTED,
    )
    due_ids = list(
        accounts.exclude(analytics_snapshots__captured_at__gte=cutoff)
        .values_list("id", flat=True)
        .distinct()
    )
    for account_id in due_ids:
        sync_analytics_account.delay(str(account_id))
