from django.test import TestCase

import requests_mock
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from archiefvernietigingscomponent.tests.utils import (
    generate_oas_component,
    mock_service_oas_get,
    paginated_response,
)

from ..service import fetch_resultaat, get_zaken, update_zaak

ZAKEN_ROOT = "https://oz.nl/zaken/api/v1/"
CATALOGI_ROOT = "https://oz.nl/catalogi/api/v1/"
SELECTIELIJST_ROOT = "https://oz.nl/selectielijst/api/v1/"

ZAAKTYPE_1 = {
    "url": f"{CATALOGI_ROOT}zaaktypen/uuid-1",
    "omschrijving": "A great zaaktype",
    "versiedatum": "2020-10-10",
}
ZAAKTYPE_2 = {
    "url": f"{CATALOGI_ROOT}zaaktypen/uuid-2",
    "omschrijving": "A magnificent zaaktype",
    "versiedatum": "2020-08-08",
    "selectielijstProcestype": f"{SELECTIELIJST_ROOT}procestypen/uuid-1",
}
ZAKEN = [
    {
        "url": f"{ZAKEN_ROOT}1",
        "identificatie": "ZAAK-2020-0000000001",
        "omschrijving": "test1",
        "zaaktype": ZAAKTYPE_1["url"],
        "bronorganisatie": "095847261",
        "startdatum": "2020-12-12",
        "registratiedatum": "2020-11-12",
    },
    {
        "url": f"{ZAKEN_ROOT}2",
        "identificatie": "ZAAK-2020-0000000002",
        "omschrijving": "test2",
        "zaaktype": ZAAKTYPE_1["url"],
        "bronorganisatie": "517439943",
        "startdatum": "2020-11-12",
        "registratiedatum": "2020-10-12",
    },
    {
        "url": f"{ZAKEN_ROOT}3",
        "identificatie": "ZAAK-2020-0000000003",
        "omschrijving": "test3",
        "zaaktype": ZAAKTYPE_2["url"],
        "bronorganisatie": "095847261",
        "startdatum": "2020-11-12",
        "registratiedatum": "2020-10-12",
    },
    {
        "url": f"{ZAKEN_ROOT}4",
        "identificatie": "ZAAK-2020-0000000004",
        "omschrijving": "test4",
        "zaaktype": ZAAKTYPE_2["url"],
        "bronorganisatie": "517439943",
        "startdatum": "2020-12-12",
        "registratiedatum": "2020-10-12",
    },
]


@requests_mock.Mocker()
class ServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        Service.objects.create(api_type=APITypes.zrc, api_root=ZAKEN_ROOT)

    def _setUpMock(self, m):
        zaak = generate_oas_component("zrc", "schemas/Zaak", url=f"{ZAKEN_ROOT}5",)

        mock_service_oas_get(m, ZAKEN_ROOT, "zrc")
        m.patch(f"{ZAKEN_ROOT}5", json=zaak)

    def test_update_zaak(self, m):
        self._setUpMock(m)
        data = {
            "archiefnominatie": "blijvend_bewaren",
            "archiefactiedatum": "2020-06-17",
        }

        zaak = update_zaak(f"{ZAKEN_ROOT}5", data, "Change archive params")

        self.assertEqual(zaak["url"], f"{ZAKEN_ROOT}5")
        self.assertEqual(m.last_request.url, f"{ZAKEN_ROOT}5")
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


@requests_mock.Mocker()
class ServiceGetZakenTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Service.objects.create(
            label="Catalogi API",
            api_type=APITypes.ztc,
            api_root=CATALOGI_ROOT,
            oas="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        Service.objects.create(
            label="Zaken API",
            api_type=APITypes.zrc,
            api_root=ZAKEN_ROOT,
            oas="https://oz.nl/zaken/api/v1/schema/openapi.json",
        )
        Service.objects.create(
            label="Selectielijst API",
            api_type=APITypes.orc,
            api_root=SELECTIELIJST_ROOT,
            oas="https://oz.nl/selectielijst/api/v1/schema/openapi.json",
        )

    def _set_up_mocks(self, m):
        mock_service_oas_get(
            m, CATALOGI_ROOT, "ztc", oas_url=f"{CATALOGI_ROOT}schema/openapi.json",
        )
        mock_service_oas_get(
            m, ZAKEN_ROOT, "zrc", oas_url=f"{ZAKEN_ROOT}schema/openapi.json",
        )
        mock_service_oas_get(
            m,
            SELECTIELIJST_ROOT,
            "selectielijst",
            oas_url=f"{SELECTIELIJST_ROOT}schema/openapi.json",
        )

    def test_retrieve_ordered_zaken(self, m):
        self._set_up_mocks(m)
        m.get(
            f"{ZAKEN_ROOT}zaken?archiefactiedatum__isnull=true&einddatum__isnull=false",
            json=paginated_response(ZAKEN),
        )
        m.get(
            url=f"{CATALOGI_ROOT}zaaktypen",
            json=paginated_response([ZAAKTYPE_1, ZAAKTYPE_2]),
        )

        zaken = get_zaken(
            query_params={"einddatum__isnull": False, "archiefactiedatum__isnull": True}
        )

        for zaak in zaken:
            self.assertIsInstance(zaak["zaaktype"], dict)

        # Order on registratiedatum, then on startdatum, then on identificatie and then reversed
        zaken_expected_order = ["test1", "test4", "test3", "test2"]
        zaken_order = [zaak["omschrijving"] for zaak in zaken]

        self.assertEqual(zaken_expected_order, zaken_order)
