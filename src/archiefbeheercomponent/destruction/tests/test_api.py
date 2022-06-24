from django.test import TransactionTestCase, override_settings
from django.urls import reverse

import requests_mock
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.constants import RoleTypeChoices
from archiefbeheercomponent.destruction.models import ArchiveConfig
from archiefbeheercomponent.destruction.tests.factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
    DestructionListItemFactory,
)
from archiefbeheercomponent.tests.utils import mock_service_oas_get, paginated_response

ZAKEN_ROOT = "https://oz.nl/zaken/api/v1/"
CATALOGI_ROOT = "https://oz.nl/catalogi/api/v1/"
SELECTIELIJST_ROOT = "https://oz.nl/selectielijst/api/v1/"

ZAAK_1 = {
    "url": f"{ZAKEN_ROOT}zaken/uuid-1",
    "uuid": "uuid-1",
    "bronorganisatie": "123456789",
    "identificatie": "ZAAK-001",
    "omschrijving": "A nice zaak",
    "archiefnominatie": "vernietigen",
    "startdatum": "2020-01-01",
    "einddatum": "2020-01-11",
    "archiefactiedatum": "2021-01-01",
    "relevanteAndereZaken": [],
    "zaaktype": f"{CATALOGI_ROOT}zaaktypen/uuid-1",
}

ZAAK_2 = {
    "url": f"{ZAKEN_ROOT}zaken/uuid-2",
    "uuid": "uuid-2",
    "bronorganisatie": "987654321",
    "identificatie": "ZAAK-002",
    "omschrijving": "A beautiful zaak",
    "archiefnominatie": "vernietigen",
    "startdatum": "2020-01-01",
    "einddatum": "2020-01-11",
    "archiefactiedatum": "2021-02-01",
    "relevanteAndereZaken": [
        {"url": f"{ZAKEN_ROOT}zaken/uuid-3", "aardRelatie": "vervolg"}
    ],
    "zaaktype": f"{CATALOGI_ROOT}zaaktypen/uuid-2",
}

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

SELECTIELIJST = {
    "url": f"{SELECTIELIJST_ROOT}procestypen/uuid-1",
    "nummer": 1,
}


@requests_mock.Mocker()
@override_settings(LANGUAGE_CODE="en")
class FetchListItemsTests(TransactionTestCase):
    def _set_up_services(self):
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
            m,
            CATALOGI_ROOT,
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        mock_service_oas_get(
            m,
            ZAKEN_ROOT,
            "zrc",
            oas_url=f"{ZAKEN_ROOT}schema/openapi.json",
        )
        mock_service_oas_get(
            m,
            SELECTIELIJST_ROOT,
            "selectielijst",
            oas_url=f"{SELECTIELIJST_ROOT}schema/openapi.json",
        )
        m.get(
            url=f"{CATALOGI_ROOT}zaaktypen",
            json=paginated_response([ZAAKTYPE_1, ZAAKTYPE_2]),
        )
        m.get(
            url=f"{CATALOGI_ROOT}zaaktypen/uuid-1",
            json=ZAAKTYPE_1,
        )
        m.get(
            url=f"{CATALOGI_ROOT}zaaktypen/uuid-2",
            json=ZAAKTYPE_2,
        )
        m.get(
            url=f"{ZAKEN_ROOT}zaken/uuid-1",
            json=ZAAK_1,
        )
        m.get(
            url=f"{ZAKEN_ROOT}zaken/uuid-2",
            json=ZAAK_2,
        )
        m.get(
            url=f"{SELECTIELIJST_ROOT}procestypen/uuid-1",
            json=SELECTIELIJST,
        )

    def test_user_unauthenticated_cant_access(self, m):
        destruction_list = DestructionListFactory.create()
        url = reverse("destruction:fetch-list-items", args=[destruction_list.id])

        response = self.client.get(url)

        self.assertEqual(302, response.status_code)
        self.assertEqual(f"/admin/login/?next={url}", response.url)

    def test_returns_list_items_and_zaak_data(self, m):
        self._set_up_services()

        user = UserFactory.create(
            username="user",
            password="user",
            email="aaa@aaa.aaa",
            role__can_start_destruction=True,
            role__can_review_destruction=True,
        )

        destruction_list = DestructionListFactory.create(author=user, assignee=user)
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_1["url"]
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_2["url"]
        )

        self._set_up_mocks(m)

        url = reverse("destruction:fetch-list-items", args=[destruction_list.id])

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        response_data = response.json()

        self.assertIn("items", response_data)
        self.assertEqual(2, len(response_data["items"]))

        # Test first item (No related zaken, no process type)
        zaak_1_data = response_data["items"][0]["zaak"]
        self.assertEqual(f"{ZAKEN_ROOT}zaken/uuid-1", zaak_1_data["url"])
        self.assertEqual([], zaak_1_data["relevanteAndereZaken"])
        self.assertNotIn("processtype", zaak_1_data["zaaktype"])
        self.assertEqual("10 days", zaak_1_data["looptijd"])

        # Test second item (related zaken and process type)
        zaak_2_data = response_data["items"][1]["zaak"]
        self.assertEqual(f"{ZAKEN_ROOT}zaken/uuid-2", zaak_2_data["url"])
        self.assertEqual(
            zaak_2_data["relevanteAndereZaken"],
            [{"url": f"{ZAKEN_ROOT}zaken/uuid-3", "aardRelatie": "vervolg"}],
        )
        self.assertIn("processtype", zaak_2_data["zaaktype"])

    def test_sensitive_data_for_process_owner(self, m):
        self._set_up_services()

        record_manager = UserFactory.create(
            role__can_start_destruction=True,
            role__type=RoleTypeChoices.record_manager,
        )
        process_owner = UserFactory.create(
            role__can_review_destruction=True,
            role__type=RoleTypeChoices.process_owner,
        )

        destruction_list = DestructionListFactory.create(
            author=record_manager,
            assignee=process_owner,
            contains_sensitive_info=True,
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_1["url"]
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_2["url"]
        )

        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=process_owner
        )

        self._set_up_mocks(m)

        url = reverse("destruction:fetch-list-items", args=[destruction_list.id])

        self.client.force_login(process_owner)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        response_data = response.json()

        self.assertIn("items", response_data)
        self.assertEqual(2, len(response_data["items"]))

        # Even if the list contains sensitive data, the process owner should be able to see it
        zaak_1_data = response_data["items"][0]["zaak"]
        self.assertIn("omschrijving", zaak_1_data)

        zaak_2_data = response_data["items"][1]["zaak"]
        self.assertIn("omschrijving", zaak_2_data)

    def test_no_sensitive_data_for_process_owner(self, m):
        self._set_up_services()

        record_manager = UserFactory.create(
            role__can_start_destruction=True,
            role__type=RoleTypeChoices.record_manager,
        )
        process_owner = UserFactory.create(
            role__can_review_destruction=True,
            role__type=RoleTypeChoices.process_owner,
        )

        destruction_list = DestructionListFactory.create(
            author=record_manager,
            assignee=process_owner,
            contains_sensitive_info=False,
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_1["url"]
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_2["url"]
        )

        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=process_owner
        )

        self._set_up_mocks(m)

        url = reverse("destruction:fetch-list-items", args=[destruction_list.id])

        self.client.force_login(process_owner)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        response_data = response.json()

        self.assertIn("items", response_data)
        self.assertEqual(2, len(response_data["items"]))

        # Since the list does NOT contain sensitive data, the process owner can see it
        zaak_1_data = response_data["items"][0]["zaak"]
        self.assertIn("omschrijving", zaak_1_data)

        zaak_2_data = response_data["items"][1]["zaak"]
        self.assertIn("omschrijving", zaak_2_data)

    def test_sensitive_data_for_archivist(self, m):
        self._set_up_services()

        record_manager = UserFactory.create(
            role__can_start_destruction=True,
            role__type=RoleTypeChoices.record_manager,
        )
        archivist = UserFactory.create(
            role__can_review_destruction=True,
            role__type=RoleTypeChoices.archivist,
        )

        destruction_list = DestructionListFactory.create(
            author=record_manager,
            assignee=archivist,
            contains_sensitive_info=True,
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_1["url"]
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_2["url"]
        )

        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=archivist
        )

        self._set_up_mocks(m)

        url = reverse("destruction:fetch-list-items", args=[destruction_list.id])

        self.client.force_login(archivist)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        response_data = response.json()

        self.assertIn("items", response_data)
        self.assertEqual(2, len(response_data["items"]))

        # The list contains sensitive data, the archivist should NOT be able to see it
        zaak_1_data = response_data["items"][0]["zaak"]
        self.assertNotIn("omschrijving", zaak_1_data)

        zaak_2_data = response_data["items"][1]["zaak"]
        self.assertNotIn("omschrijving", zaak_2_data)

    def test_no_sensitive_data_for_archivist(self, m):
        self._set_up_services()

        record_manager = UserFactory.create(
            role__can_start_destruction=True,
            role__type=RoleTypeChoices.record_manager,
        )
        archivist = UserFactory.create(
            role__can_review_destruction=True,
            role__type=RoleTypeChoices.archivist,
        )

        destruction_list = DestructionListFactory.create(
            author=record_manager,
            assignee=archivist,
            contains_sensitive_info=False,
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_1["url"]
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_2["url"]
        )

        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=archivist
        )

        self._set_up_mocks(m)

        url = reverse("destruction:fetch-list-items", args=[destruction_list.id])

        self.client.force_login(archivist)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        response_data = response.json()

        self.assertIn("items", response_data)
        self.assertEqual(2, len(response_data["items"]))

        # Since the list does NOT contain sensitive data, the archivist can see it
        zaak_1_data = response_data["items"][0]["zaak"]
        self.assertIn("omschrijving", zaak_1_data)

        zaak_2_data = response_data["items"][1]["zaak"]
        self.assertIn("omschrijving", zaak_2_data)

    def test_zaakafhandelcomponent_link(self, m):
        self._set_up_services()

        config = ArchiveConfig.get_solo()
        config.link_to_zac = (
            "http://example.nl/{{ bronorganisatie }}/{{ identificatie }}/{{ uuid }}"
        )
        config.save()

        user = UserFactory.create(
            username="user",
            password="user",
            email="aaa@aaa.aaa",
            role__can_start_destruction=True,
            role__can_review_destruction=True,
        )

        destruction_list = DestructionListFactory.create(author=user, assignee=user)
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_1["url"]
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=ZAAK_2["url"]
        )

        self._set_up_mocks(m)

        url = reverse("destruction:fetch-list-items", args=[destruction_list.id])

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        response_data = response.json()

        self.assertIn("items", response_data)
        self.assertEqual(2, len(response_data["items"]))

        zaak_1_data = response_data["items"][0]["zaak"]
        self.assertIn("zac_link", zaak_1_data)
        self.assertEqual(
            "http://example.nl/123456789/ZAAK-001/uuid-1", zaak_1_data["zac_link"]
        )

        zaak_2_data = response_data["items"][1]["zaak"]
        self.assertIn("zac_link", zaak_2_data)
        self.assertEqual(
            "http://example.nl/987654321/ZAAK-002/uuid-2", zaak_2_data["zac_link"]
        )

    def test_retrieve_missing_zaak(self, m):
        self._set_up_services()
        self._set_up_mocks(m)

        user = UserFactory.create(
            username="user",
            password="user",
            email="aaa@aaa.aaa",
            role__can_start_destruction=True,
            role__can_review_destruction=True,
        )

        destruction_list = DestructionListFactory.create(author=user, assignee=user)
        missing_zaak_url = f"{ZAKEN_ROOT}zaken/uuid-3"
        DestructionListItemFactory.create(
            destruction_list=destruction_list, zaak=missing_zaak_url
        )
        m.get(missing_zaak_url, status_code=404)

        url = reverse("destruction:fetch-list-items", args=[destruction_list.id])

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertIn("error", response.json())
