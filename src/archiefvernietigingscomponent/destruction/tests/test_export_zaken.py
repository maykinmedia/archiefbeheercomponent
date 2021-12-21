from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from furl import furl

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory


class ExportZakenWithoutArchiveDateTests(TestCase):
    def test_cant_access_without_can_start_destruction(self):
        user = UserFactory(role__can_start_destruction=False)
        self.client.force_login(user)
        url = reverse("destruction:export-zaken-without-archive-date")

        response = self.client.get(url)

        self.assertEqual(403, response.status_code)

    @patch(
        "archiefvernietigingscomponent.destruction.views.export.fetch_zaken",
        return_value=[
            {
                "identificatie": "ZAAK-01",
                "omschrijving": "Test zaak 1",
                "zaaktype": {"omschrijving": "Zaaktype-1"},
            },
            {
                "identificatie": "ZAAK-02",
                "omschrijving": "Test zaak 2",
                "zaaktype": {"omschrijving": "Zaaktype-2"},
            },
        ],
    )
    @patch(
        "archiefvernietigingscomponent.destruction.views.export.uuid4",
        return_value="d0702e2c-1af4-4cb4-87d4-16632e21052e",
    )
    def test_record_manager_can_download(self, m_uuid, m_fetch_zaken):
        user = UserFactory(role__can_start_destruction=True)
        self.client.force_login(user)
        url = furl(reverse("destruction:export-zaken-without-archive-date"))
        url.args["zaken_urls"] = "http://oz.nl/zaak/1,http://oz.nl/zaak/2"

        response = self.client.get(url.url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response._headers["content-disposition"][1],
            'attachment; filename="zaken-lijst-d0702e2c-1af4-4cb4-87d4-16632e21052e.xlsx"',
        )
        self.assertEqual(
            response._headers["content-type"][1],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertNotEqual(0, len(response.content))
        m_fetch_zaken.assert_called_once_with(
            ["http://oz.nl/zaak/1", "http://oz.nl/zaak/2"]
        )

    def test_no_zaak_urls_query_param_raises_error(self):
        user = UserFactory(role__can_start_destruction=True)
        self.client.force_login(user)
        url = furl(reverse("destruction:export-zaken-without-archive-date"))

        response = self.client.get(url.url)

        self.assertEqual(400, response.status_code)
