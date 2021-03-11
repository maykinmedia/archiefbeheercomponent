import copy
from unittest.mock import patch

from django.test import TestCase

from archiefvernietigingscomponent.destruction.utils import get_additional_zaak_info

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

RESULTAAT = {
    "url": f"{ZAKEN_ROOT}resultaten/uuid-1",
    "resultaattype": {"url": f"{CATALOGI_ROOT}resultaattypen/uuid-1"},
}


SELECTIELIJST = {
    "url": f"{SELECTIELIJST_ROOT}procestypen/uuid-1",
    "nummer": 1,
}


@patch(
    "archiefvernietigingscomponent.destruction.utils.fetch_process_type",
    return_value=copy.deepcopy(SELECTIELIJST),
)
@patch(
    "archiefvernietigingscomponent.destruction.utils.get_looptijd", return_value=10,
)
@patch(
    "archiefvernietigingscomponent.destruction.utils.fetch_resultaat",
    return_value=copy.deepcopy(RESULTAAT),
)
class GetAdditionalZaakInfoTests(TestCase):
    def setUp(self) -> None:
        self.zaak_1 = {
            "url": f"{ZAKEN_ROOT}zaken/uuid-1",
            "identificatie": "ZAAK-001",
            "omschrijving": "A nice zaak",
            "archiefnominatie": "vernietigen",
            "startdatum": "2020-01-01",
            "einddatum": "2020-01-11",
            "archiefactiedatum": "2021-01-01",
            "relevanteAndereZaken": [],
            "zaaktype": ZAAKTYPE_1,
            "resultaat": RESULTAAT["url"],
        }

        self.zaak_2 = {
            "url": f"{ZAKEN_ROOT}zaken/uuid-2",
            "identificatie": "ZAAK-002",
            "omschrijving": "A beautiful zaak",
            "archiefnominatie": "vernietigen",
            "startdatum": "2020-01-01",
            "einddatum": "2020-01-11",
            "archiefactiedatum": "2021-02-01",
            "relevanteAndereZaken": [
                {"url": f"{ZAKEN_ROOT}zaken/uuid-3", "aardRelatie": "vervolg"}
            ],
            "zaaktype": ZAAKTYPE_2,
        }

    def test_looptijd(self, m_fetch_resultaat, m_get_looptijd, m_fetch_process_type):
        additional_zaak_data = get_additional_zaak_info(self.zaak_1)

        self.assertEqual("10 days", additional_zaak_data["looptijd"])

    def test_no_process_type(
        self, m_fetch_resultaat, m_get_looptijd, m_fetch_process_type
    ):
        self.assertNotIn("selectielijstProcestype", self.zaak_1["zaaktype"])

        additional_zaak_data = get_additional_zaak_info(self.zaak_1)

        self.assertNotIn("processttype", additional_zaak_data["zaaktype"])
        m_fetch_process_type.assert_not_called()

    def test_with_process_type(
        self, m_fetch_resultaat, m_get_looptijd, m_fetch_process_type
    ):
        self.assertEqual(
            f"{SELECTIELIJST_ROOT}procestypen/uuid-1",
            ZAAKTYPE_2["selectielijstProcestype"],
        )

        additional_zaak_data = get_additional_zaak_info(self.zaak_2)

        self.assertEqual(
            {"nummer": 1}, additional_zaak_data["zaaktype"]["processttype"]
        )
        m_fetch_process_type.assert_called_once()

    def test_no_resultaat(
        self, m_fetch_resultaat, m_get_looptijd, m_fetch_process_type
    ):
        self.assertNotIn("resultaat", self.zaak_2)

        additional_zaak_data = get_additional_zaak_info(self.zaak_2)

        self.assertNotIn("resultaat", additional_zaak_data)

    def test_with_resultaat(
        self, m_fetch_resultaat, m_get_looptijd, m_fetch_process_type
    ):
        self.assertIn("resultaat", self.zaak_1)
        self.assertTrue(isinstance(self.zaak_1["resultaat"], str))

        additional_zaak_data = get_additional_zaak_info(self.zaak_1)

        self.assertEqual(RESULTAAT, additional_zaak_data["resultaat"])
        m_fetch_resultaat.assert_called_once()
