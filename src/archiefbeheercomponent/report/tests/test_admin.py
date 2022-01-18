from django.urls import reverse

from django_webtest import WebTest

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.report.tests.factories import DestructionReportFactory


class DestructionReportAdminTests(WebTest):
    def test_links_to_report_work(self):
        superuser = UserFactory.create(is_staff=True, is_superuser=True)
        report = DestructionReportFactory.create()

        url = reverse("admin:report_destructionreport_change", args=[report.pk])

        response = self.app.get(url, user=superuser)

        self.assertEqual(200, response.status_code)

        url = reverse("report:download-report", args=[report.pk])
        download_pdf_url = f"{url}?type=pdf"
        download_csv_url = f"{url}?type=csv"

        links = response.html.find_all("a")

        contains_link_to_pdf = False
        contains_link_to_csv = False
        for link in links:
            if link.attrs["href"] == download_csv_url:
                contains_link_to_csv = True
            elif link.attrs["href"] == download_pdf_url:
                contains_link_to_pdf = True

        self.assertTrue(contains_link_to_pdf)
        self.assertTrue(contains_link_to_csv)

        response = self.app.get(download_pdf_url, user=superuser)

        self.assertEqual(200, response.status_code)
        self.assertGreater(len(response.content), 0)

        response = self.app.get(download_csv_url, user=superuser)

        self.assertEqual(200, response.status_code)
        self.assertGreater(len(response.content), 0)

    def test_cant_add_report(self):
        superuser = UserFactory.create(is_staff=True, is_superuser=True)
        self.client.force_login(superuser)

        url = reverse("admin:report_destructionreport_add")

        response = self.client.get(url)

        self.assertEqual(403, response.status_code)

    def test_superuser_without_role_can_download(self):
        superuser = UserFactory.create(is_staff=True, is_superuser=True)
        superuser.role = None
        superuser.save()

        report = DestructionReportFactory.create()

        url = reverse("admin:report_destructionreport_change", args=[report.pk])

        response = self.app.get(url, user=superuser)

        self.assertEqual(200, response.status_code)

        url = reverse("report:download-report", args=[report.pk])

        response = self.app.get(f"{url}?type=pdf", user=superuser)

        self.assertEqual(200, response.status_code)
        self.assertGreater(len(response.content), 0)
