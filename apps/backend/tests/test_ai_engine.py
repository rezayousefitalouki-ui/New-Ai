import json
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from apps.ai_engine.models import AIGeneration
from apps.ai_engine.provider import ProviderError, generate
from apps.ai_engine.tasks import run_generation
from apps.workspaces.models import Membership, Workspace

User = get_user_model()


class _FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _size=-1):
        return self.payload


def _brand():
    return SimpleNamespace(
        business_name="نمونه",
        industry="فروشگاه",
        products="محصول",
        audience="مخاطب",
        voice="friendly",
        preferred_topics=[],
        forbidden_terms=[],
    )


class AIProviderTests(SimpleTestCase):
    @override_settings(
        AI_PROVIDER_API_KEY="test-key",
        AI_PROVIDER_MODEL="test-model",
        AI_PROVIDER_BASE_URL="https://api.example.test/v1",
        AI_PROVIDER_TIMEOUT_SECONDS=10,
    )
    @patch("apps.ai_engine.provider.urlopen")
    def test_parses_valid_structured_ideas(self, urlopen):
        urlopen.return_value = _FakeResponse({
            "choices": [{"message": {"content": json.dumps({"items": [{"title": "ایده"}]})}}],
            "usage": {"total_tokens": 42},
        })

        result, model, usage = generate("ideas", "یک ایده بساز", _brand())

        self.assertEqual(result["items"][0]["title"], "ایده")
        self.assertEqual(model, "test-model")
        self.assertEqual(usage, 42)
        self.assertIn("Bearer test-key", urlopen.call_args.args[0].headers.values())

    @override_settings(
        AI_PROVIDER_API_KEY="",
        AI_PROVIDER_MODEL="",
        AI_PROVIDER_BASE_URL="https://api.example.test/v1",
        AI_PROVIDER_TIMEOUT_SECONDS=10,
    )
    def test_missing_provider_configuration_is_a_safe_error(self):
        with self.assertRaises(ProviderError):
            generate("caption", "متن", _brand())

    @override_settings(
        AI_PROVIDER_API_KEY="test-key",
        AI_PROVIDER_MODEL="test-model",
        AI_PROVIDER_BASE_URL="http://example.test/v1",
        AI_PROVIDER_TIMEOUT_SECONDS=10,
    )
    def test_rejects_non_https_provider_endpoint(self):
        with self.assertRaises(ProviderError):
            generate("caption", "متن", _brand())

    @override_settings(
        AI_PROVIDER_API_KEY="test-key",
        AI_PROVIDER_MODEL="test-model",
        AI_PROVIDER_BASE_URL="https://api.example.test/v1",
        AI_PROVIDER_TIMEOUT_SECONDS=10,
    )
    @patch("apps.ai_engine.provider.urlopen")
    def test_rejects_malformed_kind_specific_output(self, urlopen):
        urlopen.return_value = _FakeResponse({
            "choices": [{"message": {"content": json.dumps({"caption": "wrong shape"})}}],
        })
        with self.assertRaises(ProviderError):
            generate("ideas", "ایده", _brand())


class AIWorkspaceAccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(phone="09120000001", password="test-password")
        self.viewer = User.objects.create_user(phone="09120000002", password="test-password")
        self.other_user = User.objects.create_user(phone="09120000003", password="test-password")
        self.workspace = Workspace.objects.create(name="فضای اول", slug="workspace-one")
        self.private_workspace = Workspace.objects.create(name="فضای خصوصی", slug="workspace-private")
        Membership.objects.create(
            workspace=self.workspace, user=self.owner, role=Membership.Role.OWNER
        )
        Membership.objects.create(
            workspace=self.workspace, user=self.viewer, role=Membership.Role.VIEWER
        )
        Membership.objects.create(
            workspace=self.private_workspace,
            user=self.other_user,
            role=Membership.Role.OWNER,
        )
        self.generation = AIGeneration.objects.create(
            workspace=self.workspace,
            created_by=self.owner,
            kind=AIGeneration.Kind.IDEAS,
            brief="ایده برای محصول",
        )
        self.private_generation = AIGeneration.objects.create(
            workspace=self.private_workspace,
            created_by=self.other_user,
            kind=AIGeneration.Kind.CAPTION,
            brief="اطلاعات خصوصی",
        )
        self.client = APIClient()

    def test_generation_list_is_scoped_to_member_workspace(self):
        self.client.force_authenticate(self.owner)

        response = self.client.get(
            "/api/v1/ai/generations/",
            {"workspace_id": str(self.workspace.id)},
        )

        self.assertEqual(response.status_code, 200)
        returned_ids = {row["id"] for row in response.json()["generations"]}
        self.assertEqual(returned_ids, {str(self.generation.id)})
        self.assertNotIn(str(self.private_generation.id), returned_ids)

    def test_non_member_cannot_list_another_workspace(self):
        self.client.force_authenticate(self.owner)

        response = self.client.get(
            "/api/v1/ai/generations/",
            {"workspace_id": str(self.private_workspace.id)},
        )

        self.assertEqual(response.status_code, 404)

    def test_viewer_cannot_start_generation(self):
        self.client.force_authenticate(self.viewer)

        response = self.client.post(
            "/api/v1/ai/generations/",
            {
                "workspace_id": str(self.workspace.id),
                "kind": "ideas",
                "brief": "ایده برای محصول",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    @patch("apps.ai_engine.api.run_generation.delay")
    def test_writer_queues_generation_after_transaction_commit(self, enqueue):
        self.client.force_authenticate(self.owner)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                "/api/v1/ai/generations/",
                {
                    "workspace_id": str(self.workspace.id),
                    "kind": "caption",
                    "brief": "برای محصول یک کپشن بنویس",
                },
                format="json",
            )

        self.assertEqual(response.status_code, 202)
        enqueue.assert_called_once_with(response.json()["generation"]["id"])

    @patch("apps.ai_engine.tasks.generate", side_effect=RuntimeError("provider crashed"))
    def test_unexpected_task_error_does_not_leave_generation_running(self, _generate):
        run_generation(str(self.generation.id))

        self.generation.refresh_from_db()
        self.assertEqual(self.generation.status, AIGeneration.Status.FAILED)
        self.assertTrue(self.generation.error_message)
        self.assertNotIn("provider crashed", self.generation.error_message)
