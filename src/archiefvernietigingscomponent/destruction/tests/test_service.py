from django.test import TestCase

import requests_mock
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from archiefvernietigingscomponent.tests.utils import (
    generate_oas_component,
    mock_service_oas_get,
)

from ..service import fetch_resultaat, update_zaak

ZAKEN_ROOT = "https://api.zaken.nl/api/v1/"
ZAAK_URL = f"{ZAKEN_ROOT}zaken/17e08a91-67ff-401d-aae1-69b1beeeff06"

CATALOGI_ROOT = "https://api.catalogi.nl/api/v1/"


@requests_mock.Mocker()
class ServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        Service.objects.create(api_type=APITypes.zrc, api_root=ZAKEN_ROOT)

    def _setUpMock(self, m):
        zaak = generate_oas_component("zrc", "schemas/Zaak", url=ZAAK_URL,)

        mock_service_oas_get(m, ZAKEN_ROOT, "zrc")
        m.patch(ZAAK_URL, json=zaak)

    def test_update_zaak(self, m):
        self._setUpMock(m)
        data = {
            "archiefnominatie": "blijvend_bewaren",
            "archiefactiedatum": "2020-06-17",
        }

        zaak = update_zaak(ZAAK_URL, data, "Change archive params")

        self.assertEqual(zaak["url"], ZAAK_URL)
        self.assertEqual(m.last_request.url, ZAAK_URL)
        self.assertEqual(m.last_request.method, "PATCH")
        self.assertEqual(m.last_request.json(), data)

        headers = m.last_request.headers
        self.assertEqual(
            headers["X-Audit-Toelichting"],
            "[Archiefvernietigingscomponent] Change archive params",
        )

    def test_fetch_resultaat(self, m):
        resultaat_url = f"{ZAKEN_ROOT}resultaten/uuid-1"
        resultaattype_url = f"{CATALOGI_ROOT}resultaattypen/uuid-1"

        Service.objects.create(api_type=APITypes.ztc, api_root=CATALOGI_ROOT)

        m.get(resultaat_url, json={"resultaattype": resultaattype_url})
        m.get(resultaattype_url, json={"url": resultaattype_url})
        mock_service_oas_get(m, ZAKEN_ROOT, "zrc")
        mock_service_oas_get(m, CATALOGI_ROOT, "ztc")

        resultaat = fetch_resultaat(resultaat_url)

        self.assertIn("resultaattype", resultaat)
        self.assertIn("url", resultaat["resultaattype"])
