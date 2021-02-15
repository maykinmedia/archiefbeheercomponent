from django.test import TestCase

import requests_mock
from freezegun import freeze_time
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory
from archiefvernietigingscomponent.constants import RoleTypeChoices
from archiefvernietigingscomponent.destruction.constants import (
    ListItemStatus,
    ListStatus,
    ReviewStatus,
)
from archiefvernietigingscomponent.destruction.tests.factories import (
    DestructionListFactory,
    DestructionListItemFactory,
    DestructionListReviewFactory,
)
from archiefvernietigingscomponent.report.utils import (
    create_destruction_report,
    get_destruction_list_archivaris_comments,
    get_looptijd,
    get_process_owner_comments,
    get_vernietigings_categorie_selectielijst,
)
from archiefvernietigingscomponent.tests.utils import mock_service_oas_get


@requests_mock.Mocker()
class DestructionReportTests(TestCase):
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

    def test_destruction_report_generation(self, m):
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
            },
        )

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
                "selectielijstProcestype": "https://selectielijst.oz.nl/api/v1/procestypen/uuid-1"
            },
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
            json={
                "selectielijstProcestype": "https://selectielijst.oz.nl/api/v1/procestypen/uuid-2"
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

        report = create_destruction_report(destruction_list)

        self.assertIn("<td>ZAAK-1</td>", report)
        self.assertIn("<td>Een zaak</td>", report)
        self.assertIn("<td>366 days</td>", report)
        self.assertIn("<td>1</td>", report)
        self.assertIn("<td>Onderdeel van vernietigingslijst: Winter cases</td>", report)

        self.assertIn("<td>ZAAK-2</td>", report)
        self.assertIn("<td>Een andere zaak</td>", report)
        self.assertIn("<td>394 days</td>", report)
        self.assertIn("<td>2</td>", report)

    def test_failed_destruction_not_in_report(self, m):
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )

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
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-2",
            json={
                "selectielijstProcestype": "https://selectielijst.oz.nl/api/v1/procestypen/uuid-2"
            },
        )
        m.get(
            url="https://selectielijst.oz.nl/api/v1/procestypen/uuid-2",
            json={"nummer": 2},
        )

        report = create_destruction_report(destruction_list)

        self.assertNotIn("<td>ZAAK-1</td>", report)
        self.assertNotIn("<td>Een zaak</td>", report)
        self.assertNotIn("<td>366 days</td>", report)
        self.assertNotIn("<td>1</td>", report)

        self.assertIn("<td>ZAAK-2</td>", report)
        self.assertIn("<td>Een andere zaak</td>", report)
        self.assertIn("<td>394 days</td>", report)
        self.assertIn("<td>2</td>", report)

    def test_no_selectielijst_client(self, m):
        mock_service_oas_get(
            m,
            "https://oz.nl/catalogi/api/v1",
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        m.get(
            url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
            json={
                "selectielijstProcestype": "https://another-selectielijst.oz.nl/api/v1/procestypen/uuid-1"
            },
        )

        number = get_vernietigings_categorie_selectielijst(
            "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1"
        )

        self.assertEqual("", number)

    def test_no_process_type_url(self, m):
        mock_service_oas_get(
            m,
            "https://oz.nl/catalogi/api/v1",
            "ztc",
            oas_url="https://oz.nl/catalogi/api/v1/schema/openapi.json",
        )
        m.get(url="https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1", json={})

        number = get_vernietigings_categorie_selectielijst(
            "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1"
        )

        self.assertEqual("", number)

    def test_comments_archivaris(self, m):
        archivaris = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )

        comment = get_destruction_list_archivaris_comments(destruction_list)

        self.assertEqual("What a magnificent list!", comment)

    def test_only_comments_from_archivaris_returned(self, m):
        archivaris = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="I am happy with this list!",
        )

        comment = get_destruction_list_archivaris_comments(destruction_list)

        self.assertEqual("What a magnificent list!", comment)

    def test_only_latest_comment_from_archivaris_is_returned(self, m):
        archivaris = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="I am happy with this list!",
        )

        comment = get_destruction_list_archivaris_comments(destruction_list)

        self.assertEqual("I am happy with this list!", comment)

    def test_only_approval_comment_from_archivaris_is_returned(self, m):
        archivaris = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.changes_requested,
            author=archivaris,
            text="Could you remove the first zaak?",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="I am happy with this list now!",
        )

        comment = get_destruction_list_archivaris_comments(destruction_list)

        self.assertEqual("I am happy with this list now!", comment)

    def test_comments_process_owner(self, m):
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )

        comment = get_process_owner_comments(destruction_list)

        self.assertEqual("What a magnificent list!", comment)

    def test_only_comments_from_process_owner_returned(self, m):
        archivaris = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="I am happy with this list!",
        )

        comment = get_process_owner_comments(destruction_list)

        self.assertEqual("I am happy with this list!", comment)

    def test_only_latest_comment_from_process_owner_is_returned(self, m):
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="I am happy with this list!",
        )

        comment = get_process_owner_comments(destruction_list)

        self.assertEqual("I am happy with this list!", comment)

    def test_only_approval_comment_from_process_owner_is_returned(self, m):
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(status=ListStatus.processing)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.failed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "toelichting": "Bah",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
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
            },
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.changes_requested,
            author=process_owner,
            text="Could you remove the first zaak?",
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="I am happy with this list now!",
        )

        comment = get_process_owner_comments(destruction_list)

        self.assertEqual("I am happy with this list now!", comment)

    def test_looptijd_with_einddatum(self, m):
        zaak = {"startdatum": "2021-05-01", "einddatum": "2021-05-05"}
        loop_tijd = get_looptijd(zaak)

        self.assertEqual(4, loop_tijd)

    @freeze_time("2021-05-05")
    def test_looptijd_without_einddatum(self, m):
        zaak = {
            "startdatum": "2021-05-01",
        }
        loop_tijd = get_looptijd(zaak)

        self.assertEqual(4, loop_tijd)
