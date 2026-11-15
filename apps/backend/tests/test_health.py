from django.test import TestCase
from rest_framework.test import APIClient

class HealthEndpointTests(TestCase):
    def test_liveness_is_public(self):
        response = APIClient().get("/api/v1/health/live/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
