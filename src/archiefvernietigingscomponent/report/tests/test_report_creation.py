from django.test import TestCase, override_settings
from django.urls import reverse

import requests_mock
from freezegun import freeze_time
from privates.test import temp_private_root
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory
from archiefvernietigingscomponent.constants import RoleTypeChoices
from archiefvernietigingscomponent.destruction.constants import (
    ListItemStatus,
    ReviewStatus,
)
from archiefvernietigingscomponent.destruction.models import DestructionList
from archiefvernietigingscomponent.destruction.tests.factories import (
    DestructionListFactory,
    DestructionListItemFactory,
    DestructionListReviewFactory,
)
from archiefvernietigingscomponent.report.utils import create_destruction_report
from archiefvernietigingscomponent.tests.utils import mock_service_oas_get


@requests_mock.Mocker()
@temp_private_root()
@override_settings(LANGUAGE_CODE="en")
class CreateReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        Service.objects.create(
            label="Selectielijst API",
            api_type=APITypes.orc,
            api_root="https://selectielijst.oz.nl/api/v1",
            oas="https://selectielijst.oz.nl/api/v1/schema/openapi.json",
        )
        Service.objects.create(
            label="Catalogi API",
            api_type=APITypes.ztc,
            api_root="https://oz.nl/catalogi/api/v1",
            oas="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )

    def _setup_mocks(self, m):
        mock_service_oas_get(
            m,
            "https://selectielijst.oz.nl/api/v1",
            "selectielijst",
            oas_url="https://selectielijst.oz.nl/api/v1/schema/openapi.json",
        )
        mock_service_oas_get(
            m,
            "https://oz.nl/catalogi/api/v1",
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
            json={
                "selectielijstProcestype": "https://selectielijst.oz.nl/api/v1/procestypen/uuid-1",
                "omschrijving": "ZAAKTYPE-001",
            },
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
            json={
                "selectielijstProcestype": "https://selectielijst.oz.nl/api/v1/procestypen/uuid-2",
                "omschrijving": "ZAAKTYPE-002",
            },
        )
        m.get(
            url="https://selectielijst.oz.nl/api/v1/procestypen/uuid-1",
            json={"nummer": 1},
        )
        m.get(
            url="https://selectielijst.oz.nl/api/v1/procestypen/uuid-2",
            json={"nummer": 2},
        )

    @freeze_time("2021-05-05")
    def test_report_creation_with_process_owner(self, m):
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(
            name="Winter cases", contains_sensitive_info=False
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
                "verantwoordelijke_organisatie": "Nice organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nice result type",
                        "archiefactietermijn": "20 days",
                    }
                },
                "relevante_andere_zaken": [],
            },
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-2",
                "omschrijving": "Een andere zaak",
                "toelichting": "Boh",
                "startdatum": "2020-02-01",
                "einddatum": "2021-03-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
                "verantwoordelijke_organisatie": "Nice organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nice result type",
                        "archiefactietermijn": "20 days",
                    }
                },
                "relevante_andere_zaken": [],
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )

        self._setup_mocks(m)

        report = create_destruction_report(destruction_list)

        self.assertEqual(process_owner, report.process_owner)
        self.assertEqual(
            "Declaration of destruction - Winter cases (2021-05-05)", report.title
        )

        report.content.seek(0)
        content = report.content.read().decode("utf8")

        self.assertIn("<td>ZAAK-1</td>", content)
        self.assertIn("<td>Een zaak</td>", content)
        self.assertIn("<td>366 days</td>", content)
        self.assertIn("<td>1</td>", content)
        self.assertIn("<td>Bah</td>", content)

        self.assertIn("<td>ZAAK-2</td>", content)
        self.assertIn("<td>Een andere zaak</td>", content)
        self.assertIn("<td>394 days</td>", content)
        self.assertIn("<td>2</td>", content)
        self.assertIn("<td>Boh</td>", content)

        self.client.force_login(process_owner)
        response = self.client.get(reverse("report:download-report", args=[report.pk]))

        self.assertEqual(200, response.status_code)

    def test_report_creation_without_process_owner(self, m):
        destruction_list = DestructionListFactory.create(name="Winter cases")
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
                "verantwoordelijke_organisatie": "Nice organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nice result type",
                        "archiefactietermijn": "20 days",
                    }
                },
                "relevante_andere_zaken": [],
            },
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-2",
                "omschrijving": "Een andere zaak",
                "toelichting": "",
                "startdatum": "2020-02-01",
                "einddatum": "2021-03-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
                "verantwoordelijke_organisatie": "Nice organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nice result type",
                        "archiefactietermijn": "20 days",
                    }
                },
                "relevante_andere_zaken": [],
            },
        )

        self._setup_mocks(m)

        report = create_destruction_report(destruction_list)

        self.assertEqual(None, report.process_owner)

    def test_private_media_is_not_accessible(self, m):
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(name="Winter cases")
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
                "verantwoordelijke_organisatie": "Nice organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nice result type",
                        "archiefactietermijn": "20 days",
                    }
                },
                "relevante_andere_zaken": [],
            },
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-2",
                "omschrijving": "Een andere zaak",
                "toelichting": "",
                "startdatum": "2020-02-01",
                "einddatum": "2021-03-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
                "verantwoordelijke_organisatie": "Nice organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nice result type",
                        "archiefactietermijn": "20 days",
                    }
                },
                "relevante_andere_zaken": [],
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )

        self._setup_mocks(m)

        report = create_destruction_report(destruction_list)

        response = self.client.get(report.content.url)

        self.assertEqual(404, response.status_code)

    def test_relation_between_report_and_destructionlist(self, m):
        destruction_list = DestructionListFactory.create(name="Winter cases")
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
                "verantwoordelijke_organisatie": "Nice organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nice result type",
                        "archiefactietermijn": "20 days",
                    }
                },
                "relevante_andere_zaken": [],
            },
        )
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-2",
                "omschrijving": "Een andere zaak",
                "toelichting": "Boh",
                "startdatum": "2020-02-01",
                "einddatum": "2021-03-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
                "verantwoordelijke_organisatie": "Nice organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nice result type",
                        "archiefactietermijn": "20 days",
                    }
                },
                "relevante_andere_zaken": [],
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            text="What a magnificent list!",
        )

        self._setup_mocks(m)

        report = create_destruction_report(destruction_list)

        # can't use refresh_from_db() because of django-fsm
        destruction_list = DestructionList.objects.get(id=destruction_list.id)

        self.assertEqual(1, destruction_list.destructionreport_set.count())
        self.assertEqual(report, destruction_list.destructionreport_set.get())
