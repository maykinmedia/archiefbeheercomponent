from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse_lazy

from rma.accounts.tests.factories import UserFactory

from ..models import ArchiveConfig

ZAAKTYPE = "https://some.catalogi.nl/api/v1/zaaktypen/aaa"
ZAKEN = [
    {
        "url": "https://some.zaken.nl/api/v1/zaken/1",
        "identificatie": "ZAAK-2020-0000000001",
        "omschrijving": "test1",
        "zaaktype": ZAAKTYPE,
    },
    {
        "url": "https://some.zaken.nl/api/v1/zaken/2",
        "identificatie": "ZAAK-2020-0000000002",
        "omschrijving": "test2",
        "zaaktype": ZAAKTYPE,
    },
]


@patch("rma.destruction.api.get_zaken", return_value=ZAKEN)
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

    def test_fetch_zaken_no_filters(self, m):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"zaken": ZAKEN})

        m.assert_called_once_with(query_params=self.default_query)

    def test_fetch_zaken_filter_by_zaaktype(self, m):
        response = self.client.get(self.url, {"zaaktypen": ZAAKTYPE})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"zaken": ZAKEN})

        query = self.default_query.copy()
        query["zaaktype"] = ZAAKTYPE
        m.assert_called_once_with(query)

    def test_fetch_zaken_filter_by_start_date(self, m):
        response = self.client.get(self.url, {"startdatum": "2020-02-02"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"zaken": ZAKEN})

        query = self.default_query.copy()
        query["startdatum__gte"] = "2020-02-02"
        m.assert_called_once_with(query_params=query)
