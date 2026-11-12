from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.models import AccountSnapshot, MediaSnapshot
from apps.analytics.serializers import AccountSnapshotSerializer, MediaSnapshotSerializer
from apps.analytics.tasks import sync_analytics_account
from apps.social_accounts.models import SocialAccount
from apps.workspaces.models import Membership


def _membership(user, workspace_id):
    try:
        return Membership.objects.get(user=user, workspace_id=workspace_id)
    except (Membership.DoesNotExist, ValueError):
        return None


class AnalyticsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        if not _membership(request.user, workspace_id):
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            days = min(max(int(request.query_params.get("days", 30)), 7), 90)
        except (TypeError, ValueError):
            days = 30
        accounts = SocialAccount.objects.filter(
            workspace_id=workspace_id,
            platform=SocialAccount.Platform.INSTAGRAM,
            status=SocialAccount.Status.CONNECTED,
        )
        cutoff = timezone.now() - timedelta(days=days)
        snapshots = AccountSnapshot.objects.filter(
            social_account__workspace_id=workspace_id,
            captured_at__gte=cutoff,
        ).select_related("social_account")
        media = MediaSnapshot.objects.filter(
            social_account__workspace_id=workspace_id,
            published_at__gte=cutoff,
        ).select_related("social_account").order_by("-like_count", "-comments_count")[:20]
        latest = []
        for account in accounts:
            snapshot = AccountSnapshot.objects.filter(social_account=account).order_by("-captured_at").first()
            if snapshot:
                latest.append(snapshot)
        return Response({
            "accounts": [{"id": str(a.id), "name": a.display_name, "username": a.username, "last_error": a.last_error} for a in accounts],
            "latest": AccountSnapshotSerializer(latest, many=True).data,
            "series": AccountSnapshotSerializer(snapshots, many=True).data,
            "top_media": MediaSnapshotSerializer(media, many=True).data,
            "days": days,
            "last_updated": snapshots.order_by("-captured_at").values_list("captured_at", flat=True).first(),
        })

    def post(self, request):
        workspace_id = request.data.get("workspace_id")
        membership = _membership(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if membership.role == Membership.Role.VIEWER:
            return Response(status=status.HTTP_403_FORBIDDEN)
        accounts = SocialAccount.objects.filter(
            workspace_id=workspace_id,
            platform=SocialAccount.Platform.INSTAGRAM,
            status=SocialAccount.Status.CONNECTED,
        )
        if not accounts.exists():
            return Response({"detail": "حساب حرفه‌ای Instagram متصل‌شده‌ای پیدا نشد."}, status=400)
        for account in accounts:
            sync_analytics_account.delay(str(account.id))
        return Response({"queued": accounts.count()}, status=status.HTTP_202_ACCEPTED)
