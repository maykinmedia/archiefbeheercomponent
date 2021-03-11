import copy
from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse_lazy

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory

from ..models import ArchiveConfig
from .factories import DestructionListItemFactory

ZAAKTYPE_1 = "https://some.catalogi.nl/api/v1/zaaktypen/aaa"
ZAAKTYPE_2 = "https://some.catalogi.nl/api/v1/zaaktypen/bbb"
ZAKEN = [
    {
        "url": "https://some.zaken.nl/api/v1/zaken/1",
        "identificatie": "ZAAK-2020-0000000001",
        "omschrijving": "test1",
        "zaaktype": ZAAKTYPE_1,
        "bronorganisatie": "095847261",
    },
    {
        "url": "https://some.zaken.nl/api/v1/zaken/2",
        "identificatie": "ZAAK-2020-0000000002",
        "omschrijving": "test2",
        "zaaktype": ZAAKTYPE_1,
        "bronorganisatie": "517439943",
    },
    {
        "url": "https://some.zaken.nl/api/v1/zaken/3",
        "identificatie": "ZAAK-2020-0000000003",
        "omschrijving": "test3",
        "zaaktype": ZAAKTYPE_2,
        "bronorganisatie": "095847261",
    },
    {
        "url": "https://some.zaken.nl/api/v1/zaken/4",
        "identificatie": "ZAAK-2020-0000000004",
        "omschrijving": "test4",
        "zaaktype": ZAAKTYPE_2,
        "bronorganisatie": "517439943",
    },
]


def mock_get_additional_zaak_info(arg):
    return arg


@patch(
    "archiefvernietigingscomponent.destruction.api.get_zaken",
    return_value=copy.deepcopy(ZAKEN),
)
@patch(
    "archiefvernietigingscomponent.destruction.api.get_additional_zaak_info",
    side_effect=mock_get_additional_zaak_info,
)
class FetchZakenTests(TestCase):
    url = reverse_lazy("destruction:fetch-zaken")

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(role__can_start_destruction=True)

        cls.config = ArchiveConfig.get_solo()
        cls.config.archive_date = date(2020, 1, 1)
        cls.config.save()

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

        self.default_query = {
            "archiefnominatie": "vernietigen",
            "archiefactiedatum__lt": self.config.archive_date.isoformat(),
        }
        self.zaken_available = [
            dict(list(zaak.items()) + [["available", True]]) for zaak in ZAKEN
        ]

    def test_fetch_zaken_no_filters(self, m_get_zaak_additional_info, m_get_zaken):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"zaken": self.zaken_available})

        m_get_zaken.assert_called_once_with(query_params=self.default_query)

    def test_fetch_zaken_filter_by_zaaktype(
        self, m_get_zaak_additional_info, m_get_zaken
    ):
        response = self.client.get(self.url, {"zaaktypen": ZAAKTYPE_1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"zaken": self.zaken_available})

        query = self.default_query.copy()
        query["zaaktype"] = ZAAKTYPE_1
        m_get_zaken.assert_called_once_with(query)

    def test_fetch_zaken_filter_by_invalid_zaaktype(
        self, m_get_zaak_additional_info, m_get_zaken
    ):
        response = self.client.get(self.url, {"zaaktypen": "invalid-url"})

        self.assertEqual(response.status_code, 400)

    def test_fetch_zaken_filter_by_multiple_zaaktypen(
        self, m_get_zaak_additional_info, m_get_zaken
    ):
        response = self.client.get(
            self.url, {"zaaktypen": f"{ZAAKTYPE_1},{ZAAKTYPE_2}"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, m_get_zaken.call_count)

        query = self.default_query.copy()
        query["zaaktype"] = ZAAKTYPE_1
        self.assertEqual(m_get_zaken.call_args_list[0].args[0], query)
        query["zaaktype"] = ZAAKTYPE_2
        self.assertEqual(m_get_zaken.call_args_list[1].args[0], query)

    def test_fetch_zaken_filter_by_bronorganisatie(
        self, m_get_zaak_additional_info, m_get_zaken
    ):
        response = self.client.get(self.url, {"bronorganisaties": "095847261"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"zaken": self.zaken_available})

        query = self.default_query.copy()
        query["bronorganisatie"] = "095847261"
        m_get_zaken.assert_called_once_with(query)

    def test_fetch_zaken_filter_by_multiple_bronorganisaties(
        self, m_get_zaak_additional_info, m_get_zaken
    ):
        response = self.client.get(
            self.url, {"bronorganisaties": "095847261,517439943"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, m_get_zaken.call_count)

        query = self.default_query.copy()
        query["bronorganisatie"] = "095847261"
        self.assertEqual(m_get_zaken.call_args_list[0].args[0], query)
        query["bronorganisatie"] = "517439943"
        self.assertEqual(m_get_zaken.call_args_list[1].args[0], query)

    def test_fetch_zaken_filter_by_bronorganisatie_and_zaaktype(
        self, m_get_zaak_additional_info, m_get_zaken
    ):
        response = self.client.get(
            self.url, {"bronorganisaties": "095847261", "zaaktypen": ZAAKTYPE_1}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"zaken": self.zaken_available})

        query = self.default_query.copy()
        query["bronorganisatie"] = "095847261"
        query["zaaktype"] = ZAAKTYPE_1
        m_get_zaken.assert_called_once_with(query)

    def test_fetch_zaken_filter_by_start_date(
        self, m_get_zaak_additional_info, m_get_zaken
    ):
        response = self.client.get(self.url, {"startdatum": "2020-02-02"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"zaken": self.zaken_available})

        query = self.default_query.copy()
        query["startdatum__gte"] = "2020-02-02"
        m_get_zaken.assert_called_once_with(query_params=query)

    def test_fetch_zaken_used_in_other_dl(
        self, m_get_zaak_additional_info, m_get_zaken
    ):
        DestructionListItemFactory.create(zaak="https://some.zaken.nl/api/v1/zaken/1")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        zaak1, zaak2, zaak3, zaak4 = response.json()["zaken"]

        self.assertFalse(zaak1["available"])
        self.assertTrue(zaak2["available"])
        self.assertTrue(zaak3["available"])
        self.assertTrue(zaak4["available"])
