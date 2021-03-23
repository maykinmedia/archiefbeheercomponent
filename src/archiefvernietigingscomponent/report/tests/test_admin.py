from django.urls import reverse

from django_webtest import WebTest

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory
from archiefvernietigingscomponent.report.tests.factories import (
    DestructionReportFactory,
)


class DestructionReportAdminTests(WebTest):
    def test_link_to_report_works(self):
        superuser = UserFactory.create(is_staff=True, is_superuser=True)
        report = DestructionReportFactory.create()

        url = reverse("admin:report_destructionreport_change", args=[report.pk])

        response = self.app.get(url, user=superuser)

        self.assertEqual(200, response.status_code)

        download_url = reverse(
            "admin:report_destructionreport_content", args=[report.pk]
        )
        filename = report.content.name.split("/")[-1]
        expected_content_tag = f'<a href="{download_url}">{filename}</a>'

        self.assertIn(expected_content_tag, response.text)

        response = self.app.get(download_url, user=superuser)

        self.assertEqual(200, response.status_code)

    def test_cant_add_report(self):
        superuser = UserFactory.create(is_staff=True, is_superuser=True)
        self.client.force_login(superuser)

        url = reverse("admin:report_destructionreport_add")

        response = self.client.get(url)

        self.assertEqual(403, response.status_code)
