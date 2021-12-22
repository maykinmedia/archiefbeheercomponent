import copy
from unittest.mock import patch

from django.http.request import QueryDict
from django.test import TestCase
from django.urls import reverse

from furl import furl

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.destruction.tests.factories import (
    DestructionListItemFactory,
)

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
        "url": "https://some.zaken.nl/api/v1/zaken/1",
        "identificatie": "ZAAK-2020-0000000001",
        "omschrijving": "test1",
        "zaaktype": ZAAKTYPE_1["url"],
        "bronorganisatie": "095847261",
        "startdatum": "2020-09-12",
        "registratiedatum": "2020-12-12",
    },
    {
        "url": "https://some.zaken.nl/api/v1/zaken/2",
        "identificatie": "ZAAK-2020-0000000002",
        "omschrijving": "test2",
        "zaaktype": ZAAKTYPE_1["url"],
        "bronorganisatie": "517439943",
        "startdatum": "2020-12-12",
        "registratiedatum": "2020-11-12",
    },
    {
        "url": "https://some.zaken.nl/api/v1/zaken/3",
        "identificatie": "ZAAK-2020-0000000003",
        "omschrijving": "test3",
        "zaaktype": ZAAKTYPE_2["url"],
        "bronorganisatie": "095847261",
        "startdatum": "2020-12-12",
        "registratiedatum": "2020-10-12",
    },
    {
        "url": "https://some.zaken.nl/api/v1/zaken/4",
        "identificatie": "ZAAK-2020-0000000004",
        "omschrijving": "test4",
        "zaaktype": ZAAKTYPE_2["url"],
        "bronorganisatie": "517439943",
        "startdatum": "2020-12-12",
        "registratiedatum": "2020-09-12",
    },
]


def mock_get_additional_zaak_info(arg):
    return arg


class FetchZakenViewTests(TestCase):
    def test_view_requires_login(self):
        view_url = reverse("destruction:fetch-zaken")
        expected_redirect_url = furl(reverse("admin:login"), args={"next": view_url})

        response = self.client.get(view_url)

        self.assertRedirects(response, expected_redirect_url.url)

    @patch("archiefbeheercomponent.destruction.api.get_zaken")
    def test_fetch_zaken_no_filters(self, m):
        user = UserFactory.create(role__can_start_destruction=True)
        self.client.force_login(user)

        response = self.client.get(reverse("destruction:fetch-zaken"))

        self.assertEqual(200, response.status_code)
        m.assert_called_once_with({})

    @patch("archiefbeheercomponent.destruction.api.get_zaken")
    def test_query_params_are_forwarded(self, m):
        user = UserFactory.create(role__can_start_destruction=True)
        self.client.force_login(user)
        view_url = reverse("destruction:fetch-zaken")

        response = self.client.get(
            view_url, {"einddatum__isnull": False, "archiefactiedatum__isnull": True}
        )

        self.assertEqual(200, response.status_code)
        expected_arguments = QueryDict(
            "einddatum__isnull=False&archiefactiedatum__isnull=True", mutable=True
        )
        m.assert_called_once_with(expected_arguments)

    @patch(
        "archiefbeheercomponent.destruction.api.get_zaken",
        return_value=copy.deepcopy(ZAKEN),
    )
    @patch(
        "archiefbeheercomponent.destruction.api.get_additional_zaak_info",
        side_effect=mock_get_additional_zaak_info,
    )
    def test_fetch_zaken_used_in_other_dl(
        self, m_get_zaak_additional_info, m_get_zaken
    ):
        user = UserFactory.create(role__can_start_destruction=True)
        self.client.force_login(user)
        DestructionListItemFactory.create(zaak="https://some.zaken.nl/api/v1/zaken/1")

        response = self.client.get(reverse("destruction:fetch-zaken"))

        self.assertEqual(response.status_code, 200)
        zaak1, zaak2, zaak3, zaak4 = response.json()["zaken"]

        self.assertFalse(zaak1["available"])
        self.assertTrue(zaak2["available"])
        self.assertTrue(zaak3["available"])
        self.assertTrue(zaak4["available"])
