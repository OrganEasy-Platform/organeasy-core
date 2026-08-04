"""Testes das rotas OpenAPI / Swagger."""

from django.test import SimpleTestCase
from django.urls import reverse


class OpenApiDocsTests(SimpleTestCase):
    def test_schema_returns_openapi(self) -> None:
        response = self.client.get(reverse("schema"), {"format": "json"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["openapi"].split(".")[0], "3")
        paths = body["paths"]
        self.assertIn("/api/v1/health/", paths)
        self.assertIn("/api/v1/me/", paths)
        self.assertIn("/api/v1/me/organizations/", paths)

    def test_swagger_ui_returns_html(self) -> None:
        response = self.client.get(reverse("swagger-ui"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])
