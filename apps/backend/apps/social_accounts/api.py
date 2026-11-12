import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.social_accounts.meta_oauth import (
    MetaOAuthError,
    authorization_url,
    fetch_managed_assets,
)
from apps.social_accounts.models import OAuthState, SocialAccount
from apps.social_accounts.serializers import SocialAccountSerializer
from apps.workspaces.models import Membership, Workspace


def _membership(user, workspace_id):
    try:
        return Membership.objects.select_related("workspace").get(
            user=user,
            workspace_id=workspace_id,
        )
    except (Membership.DoesNotExist, ValueError):
        return None


def _can_manage(membership):
    return bool(
        membership and membership.role in (Membership.Role.OWNER, Membership.Role.ADMIN)
    )


class SocialAccountListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        membership = _membership(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        accounts = SocialAccount.objects.filter(
            workspace_id=workspace_id
        )
        return Response({"accounts": SocialAccountSerializer(accounts, many=True).data})


class MetaOAuthStartView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        workspace_id = request.data.get("workspace_id")
        membership = _membership(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not _can_manage(membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not (
            settings.META_APP_ID
            and settings.META_APP_SECRET
            and settings.META_GRAPH_VERSION
            and settings.META_OAUTH_CALLBACK_URI
            and settings.TOKEN_ENCRYPTION_KEY
        ):
            return Response(
                {"detail": "اتصال Meta هنوز در تنظیمات سرور فعال نشده است."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        state = secrets.token_urlsafe(32)
        OAuthState.create_for(request.user, membership.workspace, state)
        return Response({"authorization_url": authorization_url(state)})


class MetaOAuthCallbackView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        result_url = f"{settings.WEB_APP_URL.rstrip('/')}/settings/connections"
        state = request.query_params.get("state", "")
        code = request.query_params.get("code", "")
        if not state or not code or request.query_params.get("error"):
            return redirect(f"{result_url}?status=failed")
        try:
            oauth_state = OAuthState.objects.select_related("workspace", "user").get(
                state_digest=OAuthState.digest(state)
            )
        except OAuthState.DoesNotExist:
            return redirect(f"{result_url}?status=invalid_state")
        if not oauth_state.consume():
            return redirect(f"{result_url}?status=expired_state")
        try:
            assets = fetch_managed_assets(code)
            if not assets:
                return redirect(f"{result_url}?status=no_assets")
            with transaction.atomic():
                for asset in assets:
                    account, _ = SocialAccount.objects.update_or_create(
                        workspace=oauth_state.workspace,
                        platform=asset["platform"],
                        external_id=asset["external_id"],
                        defaults={
                            "display_name": asset["display_name"][:160],
                            "username": asset["username"][:160],
                            "token_expires_at": (
                                timezone.now() + timedelta(seconds=asset["expires_in"])
                                if asset["expires_in"]
                                else None
                            ),
                            "granted_scopes": settings.META_OAUTH_SCOPES,
                            "status": SocialAccount.Status.CONNECTED,
                            "connected_by": oauth_state.user,
                            "last_error": "",
                        },
                    )
                    account.set_access_token(asset["access_token"])
                    account.save(update_fields=("access_token_encrypted", "updated_at"))
        except MetaOAuthError:
            return redirect(f"{result_url}?status=provider_error")
        except ValueError:
            return redirect(f"{result_url}?status=configuration_error")
        return redirect(f"{result_url}?status=connected")
