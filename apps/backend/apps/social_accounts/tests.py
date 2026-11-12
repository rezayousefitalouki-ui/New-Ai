from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.social_accounts.models import OAuthState, SocialAccount
from apps.workspaces.models import Membership, Workspace


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.client.get(reverse("csrf"))

    def test_registration_creates_owner_workspace_and_session(self):
        response = self.client.post(
            reverse("register"),
            {
                "phone": "09123456789",
                "password": "StrongPass!2026",
                "workspace_name": "Social Studio",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(phone="09123456789")
        membership = Membership.objects.get(user=user)
        self.assertEqual(membership.role, Membership.Role.OWNER)
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_registration_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        response = client.post(
            reverse("register"),
            {
                "phone": "09123456789",
                "password": "StrongPass!2026",
                "workspace_name": "Social Studio",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_login_and_logout_use_session(self):
        User.objects.create_user(phone="09123456789", password="StrongPass!2026")
        response = self.client.post(
            reverse("login"),
            {"phone": "09123456789", "password": "StrongPass!2026"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(reverse("me")).status_code, 200)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 204)


class WorkspaceAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(phone="09123456789", password="StrongPass!2026")
        self.member = User.objects.create_user(phone="09123456780", password="StrongPass!2026")
        self.workspace = Workspace.objects.create(name="Studio", slug="studio")
        Membership.objects.create(workspace=self.workspace, user=self.owner, role="owner")
        Membership.objects.create(workspace=self.workspace, user=self.member, role="viewer")

    def test_list_is_scoped_to_membership(self):
        outsider = User.objects.create_user(phone="09123456781", password="StrongPass!2026")
        self.client.force_authenticate(outsider)
        response = self.client.get(reverse("workspace-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["workspaces"], [])

    def test_viewer_cannot_add_workspace_members(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(
            reverse("workspace-members", args=(self.workspace.id,)),
            {"phone": self.owner.phone, "role": "viewer"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class MetaOAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone="09123456789", password="StrongPass!2026")
        self.workspace = Workspace.objects.create(name="Studio", slug="studio")
        Membership.objects.create(workspace=self.workspace, user=self.user, role="owner")
        self.client.force_authenticate(self.user)

    @override_settings(
        META_APP_ID="app-id",
        META_APP_SECRET="app-secret",
        META_GRAPH_VERSION="v1.0",
        META_OAUTH_CALLBACK_URI="https://example.test/api/v1/social-accounts/oauth/meta/callback/",
        TOKEN_ENCRYPTION_KEY="MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
    )
    def test_oauth_start_is_membership_scoped_and_returns_url(self):
        response = self.client.post(
            reverse("meta-oauth-start"),
            {"workspace_id": str(self.workspace.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("authorization_url", response.data)
        self.assertEqual(OAuthState.objects.count(), 1)

    def test_state_is_single_use_and_expires(self):
        state = OAuthState.create_for(
            self.user,
            self.workspace,
            "one-time-state",
        )
        self.assertTrue(state.consume())
        self.assertFalse(state.consume())
        expired = OAuthState.objects.create(
            user=self.user,
            workspace=self.workspace,
            state_digest=OAuthState.digest("expired-state"),
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.assertFalse(expired.consume())

    @override_settings(
        META_APP_ID="app-id",
        META_APP_SECRET="app-secret",
        META_GRAPH_VERSION="v1.0",
        META_OAUTH_CALLBACK_URI="https://example.test/api/v1/social-accounts/oauth/meta/callback/",
        TOKEN_ENCRYPTION_KEY="MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
        META_OAUTH_SCOPES=["pages_show_list"],
    )
    @patch("apps.social_accounts.api.fetch_managed_assets")
    def test_callback_saves_managed_page_token_encrypted(self, fetch_assets):
        fetch_assets.return_value = [{
            "platform": "facebook",
            "external_id": "page-1",
            "display_name": "Brand Page",
            "username": "",
            "access_token": "private-page-token",
            "expires_in": 3600,
        }]
        OAuthState.create_for(self.user, self.workspace, "valid-state")
        response = self.client.get(
            reverse("meta-oauth-callback"),
            {"state": "valid-state", "code": "authorization-code"},
        )
        self.assertEqual(response.status_code, 302)
        account = SocialAccount.objects.get(workspace=self.workspace)
        self.assertNotIn("private-page-token", account.access_token_encrypted)
        self.assertEqual(account.get_access_token(), "private-page-token")
