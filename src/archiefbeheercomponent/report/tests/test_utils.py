from unittest.mock import patch

from django.test import TestCase, override_settings

from freezegun import freeze_time
from lxml.html import document_fromstring
from timeline_logger.models import TimelineLog

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.constants import RoleTypeChoices
from archiefbeheercomponent.destruction.constants import (
    ListItemStatus,
    ListStatus,
    ReviewStatus,
)
from archiefbeheercomponent.destruction.models import DestructionListReviewComment
from archiefbeheercomponent.destruction.tests.factories import (
    DestructionListFactory,
    DestructionListItemFactory,
    DestructionListReviewFactory,
)
from archiefbeheercomponent.report.utils import (
    create_audittrail_report,
    get_destruction_list_archivaris_comments,
    get_destruction_report_data,
    get_looptijd,
    get_process_owner_comments,
)


@override_settings(LANGUAGE_CODE="en")
class DestructionReportUtilsTests(TestCase):
    def test_get_looptijd_with_end_date(self):
        zaak = {"startdatum": "2021-05-01", "einddatum": "2021-05-05"}
        loop_tijd = get_looptijd(zaak)

        self.assertEqual(4, loop_tijd)

    @freeze_time("2021-05-05")
    def test_get_looptijd_without_end_date(self):
        zaak = {
            "startdatum": "2021-05-01",
        }
        loop_tijd = get_looptijd(zaak)

        self.assertEqual(4, loop_tijd)

    def test_get_destruction_list_archivaris_comments(self):
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

    def test_only_comments_from_archivaris_returned(self):
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

    def test_only_latest_comment_from_archivaris_is_returned(self):
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

    def test_only_approval_comment_from_archivaris_is_returned(self):
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

    def test_only_comments_from_process_owner_returned(self):
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

    def test_only_latest_comment_from_process_owner_is_returned(self):
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

    def test_only_approval_comment_from_process_owner_is_returned(self):
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

    def test_destruction_report_data_with_sensitive_info(self):
        destruction_list = DestructionListFactory.create(
            name="Winter cases", contains_sensitive_info=True,
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
                "verantwoordelijke_organisatie": "Nicer organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nicer result type",
                        "archiefactietermijn": "40 days",
                    }
                },
                "relevante_andere_zaken": [{"url": "http://some.zaak"}],
                "bytes_removed_documents": 10,
            },
        )
        archivaris = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )

        report_data, deleted_bytes = get_destruction_report_data(destruction_list)

        self.assertEqual(1, len(report_data))

        zaak_data = report_data[0]

        self.assertNotIn("omschrijving", zaak_data)
        self.assertNotIn("opmerkingen", zaak_data)

    @patch(
        "archiefbeheercomponent.report.utils.get_vernietigings_categorie_selectielijst",
        return_value="1",
    )
    @patch(
        "archiefbeheercomponent.report.utils.get_zaaktype",
        return_value={
            "omschrijving": "This is a zaaktype",
            "selectielijstProcestype": "some data",
        },
    )
    def test_destruction_report_data_without_sensitive_info(self, m_vcs, m_zaaktype):
        destruction_list = DestructionListFactory.create(
            name="Winter cases", contains_sensitive_info=False,
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
                "verantwoordelijke_organisatie": "Nicer organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nicer result type",
                        "archiefactietermijn": "40 days",
                    }
                },
                "relevante_andere_zaken": [{"url": "http://some.zaak"}],
                "bytes_removed_documents": 10,
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
                "bytes_removed_documents": 10,
            },
        )
        archivaris = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )

        report_data, deleted_bytes = get_destruction_report_data(destruction_list)

        self.assertEqual(2, len(report_data))

        # Test sensitive info
        self.assertIn("omschrijving", report_data[0])
        self.assertIn("opmerkingen", report_data[0])
        self.assertIn("omschrijving", report_data[1])
        self.assertIn("opmerkingen", report_data[1])

        # Test remaining info
        self.assertEqual("ZAAK-1", report_data[0]["identificatie"])
        self.assertEqual("Een zaak", report_data[0]["omschrijving"])
        self.assertEqual("366 days", report_data[0]["looptijd"])
        self.assertEqual("1", report_data[0]["vernietigings_categorie"])
        self.assertEqual("Bah", report_data[0]["toelichting"])
        self.assertEqual("What a magnificent list!", report_data[0]["opmerkingen"])
        self.assertEqual("", report_data[0]["reactie_zorgdrager"])
        self.assertEqual("This is a zaaktype", report_data[0]["zaaktype"])
        self.assertEqual("40 days", report_data[0]["archiefactietermijn"])
        self.assertEqual("Nicer result type", report_data[0]["resultaattype"])
        self.assertEqual(
            "Nicer organisation", report_data[0]["verantwoordelijke_organisatie"]
        )
        self.assertEqual("Yes", report_data[0]["relaties"])

        # Test remaining info
        self.assertEqual("ZAAK-2", report_data[1]["identificatie"])
        self.assertEqual("Een andere zaak", report_data[1]["omschrijving"])
        self.assertEqual("394 days", report_data[1]["looptijd"])
        self.assertEqual("1", report_data[1]["vernietigings_categorie"])
        self.assertEqual("Boh", report_data[1]["toelichting"])
        self.assertEqual("What a magnificent list!", report_data[1]["opmerkingen"])
        self.assertEqual("", report_data[1]["reactie_zorgdrager"])
        self.assertEqual("This is a zaaktype", report_data[1]["zaaktype"])
        self.assertEqual("20 days", report_data[1]["archiefactietermijn"])
        self.assertEqual("Nice result type", report_data[1]["resultaattype"])
        self.assertEqual(
            "Nice organisation", report_data[1]["verantwoordelijke_organisatie"]
        )
        self.assertEqual("No", report_data[1]["relaties"])

    @patch(
        "archiefbeheercomponent.report.utils.get_vernietigings_categorie_selectielijst",
        return_value="1",
    )
    @patch(
        "archiefbeheercomponent.report.utils.get_zaaktype",
        return_value={
            "omschrijving": "This is a zaaktype",
            "selectielijstProcestype": "some data",
        },
    )
    def test_destruction_report_content_generation_without_toelichting(
        self, m_vcs, m_zaaktype
    ):
        destruction_list = DestructionListFactory.create(contains_sensitive_info=False)
        DestructionListItemFactory.create(
            destruction_list=destruction_list,
            status=ListItemStatus.destroyed,
            extra_zaak_data={
                "identificatie": "ZAAK-1",
                "omschrijving": "Een zaak",
                "startdatum": "2020-01-01",
                "einddatum": "2021-01-01",
                "zaaktype": "https://oz.nl/catalogi/api/v1/zaaktypen/uuid-1",
                "verantwoordelijke_organisatie": "Nicer organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nicer result type",
                        "archiefactietermijn": "40 days",
                    }
                },
                "relevante_andere_zaken": [{"url": "http://some.zaak"}],
                "bytes_removed_documents": 10,
            },
        )

        report_data, deleted_bytes = get_destruction_report_data(destruction_list)

        self.assertEqual(1, len(report_data))

        # Test sensitive info
        self.assertIn("omschrijving", report_data[0])
        self.assertIn("opmerkingen", report_data[0])

        # Test remaining info
        self.assertEqual("ZAAK-1", report_data[0]["identificatie"])
        self.assertEqual("Een zaak", report_data[0]["omschrijving"])
        self.assertEqual("366 days", report_data[0]["looptijd"])
        self.assertEqual("1", report_data[0]["vernietigings_categorie"])
        self.assertNotIn("toelichting", report_data[0])
        self.assertEqual("", report_data[0]["opmerkingen"])
        self.assertEqual("", report_data[0]["reactie_zorgdrager"])
        self.assertEqual("This is a zaaktype", report_data[0]["zaaktype"])
        self.assertEqual("40 days", report_data[0]["archiefactietermijn"])
        self.assertEqual("Nicer result type", report_data[0]["resultaattype"])
        self.assertEqual(
            "Nicer organisation", report_data[0]["verantwoordelijke_organisatie"]
        )
        self.assertEqual("Yes", report_data[0]["relaties"])

    @patch(
        "archiefbeheercomponent.report.utils.get_vernietigings_categorie_selectielijst",
        return_value="1",
    )
    @patch(
        "archiefbeheercomponent.report.utils.get_zaaktype",
        return_value={
            "omschrijving": "This is a zaaktype",
            "selectielijstProcestype": "some data",
        },
    )
    def test_failed_destruction_not_in_report_content(self, m_vcs, m_zaaktype):
        destruction_list = DestructionListFactory.create(
            status=ListStatus.processing, contains_sensitive_info=False,
        )
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
                "verantwoordelijke_organisatie": "Nicer organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nicer result type",
                        "archiefactietermijn": "40 days",
                    }
                },
                "relevante_andere_zaken": [{"url": "http://some.zaak"}],
                "bytes_removed_documents": 10,
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
                "bytes_removed_documents": 10,
            },
        )

        report_data, deleted_bytes = get_destruction_report_data(destruction_list)

        self.assertEqual(1, len(report_data))

        self.assertEqual("ZAAK-2", report_data[0]["identificatie"])

    def test_logs_from_right_list_are_shown(self):
        record_manager = UserFactory.create(role__type=RoleTypeChoices.record_manager)
        archivaris = UserFactory.create(role__type=RoleTypeChoices.archivist)

        destruction_list_1 = DestructionListFactory.create(
            author=record_manager, name="Incredible list 1"
        )
        review_1 = DestructionListReviewFactory.create(
            destruction_list=destruction_list_1, author=archivaris
        )
        destruction_list_2 = DestructionListFactory.create(
            author=record_manager, name="Incredible list 2"
        )
        review_2 = DestructionListReviewFactory.create(
            destruction_list=destruction_list_2, author=archivaris
        )

        TimelineLog.objects.create(
            content_object=destruction_list_1,
            template="destruction/logs/created.html",
            extra_data={"n_items": 3},
            user=record_manager,
        )
        TimelineLog.objects.create(
            content_object=review_1,
            template="destruction/logs/review_created.html",
            user=archivaris,
        )
        # These should not appear in the audit trail report, because they are not related to the right list
        TimelineLog.objects.create(
            content_object=destruction_list_2,
            template="destruction/logs/created.html",
            extra_data={"n_items": 3},
            user=record_manager,
        )
        TimelineLog.objects.create(
            content_object=review_2,
            template="destruction/logs/review_created.html",
            user=archivaris,
        )

        report = create_audittrail_report(destruction_list_1)
        html_report = document_fromstring(report)

        self.assertEqual(2, len(html_report.find_class("log-item")))
        self.assertIn("Incredible list 1", report)
        self.assertNotIn("Incredible list 2", report)

    def test_logs_are_in_correct_order(self):
        record_manager = UserFactory.create(role__type=RoleTypeChoices.record_manager)
        archivaris = UserFactory.create(role__type=RoleTypeChoices.archivist)

        destruction_list = DestructionListFactory.create(author=record_manager)
        review = DestructionListReviewFactory.create(
            destruction_list=destruction_list, author=archivaris
        )

        with freeze_time("2012-01-14 12:00"):
            TimelineLog.objects.create(
                content_object=destruction_list,
                template="destruction/logs/created.html",
                extra_data={"n_items": 3},
                user=record_manager,
            )
        with freeze_time("2012-01-14 12:05"):
            TimelineLog.objects.create(
                content_object=review,
                template="destruction/logs/review_created.html",
                user=archivaris,
            )
        with freeze_time("2012-01-14 12:10"):
            TimelineLog.objects.create(
                content_object=destruction_list,
                template="destruction/logs/updated.html",
                extra_data={"n_items": 1},
                user=record_manager,
            )
        with freeze_time("2012-01-14 12:15"):
            TimelineLog.objects.create(
                content_object=destruction_list,
                template="destruction/logs/aborted.html",
                extra_data={"n_items": 3},
                user=record_manager,
            )

        report = create_audittrail_report(destruction_list)
        html_report = document_fromstring(report)

        self.assertEqual(4, len(html_report.find_class("log-item")))

        titles = html_report.find_class("log-item__title")
        times = [title.text_content() for title in titles]
        sorted_times = sorted(times)

        self.assertEqual(times, sorted_times)

    def test_logs_contain_comments(self):
        record_manager = UserFactory.create(role__type=RoleTypeChoices.record_manager)
        archivaris = UserFactory.create(role__type=RoleTypeChoices.archivist)

        destruction_list = DestructionListFactory.create(author=record_manager)
        review_1 = DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            author=archivaris,
            text="This is a comment for the author.",
        )
        author_comment = DestructionListReviewComment.objects.create(
            text="This is a comment for the reviewer.", review=review_1
        )

        review_2 = DestructionListReviewFactory.create(
            destruction_list=destruction_list, author=archivaris, text=""
        )

        TimelineLog.objects.create(
            content_object=destruction_list,
            template="destruction/logs/created.html",
            extra_data={"n_items": 3},
            user=record_manager,
        )
        TimelineLog.objects.create(
            content_object=review_1,
            template="destruction/logs/review_created.html",
            user=archivaris,
            extra_data={"n_items": 1, "text": review_1.text},
        )
        TimelineLog.objects.create(
            content_object=destruction_list,
            template="destruction/logs/updated.html",
            user=record_manager,
            extra_data={"n_items": 1, "text": author_comment.text},
        )
        TimelineLog.objects.create(
            content_object=review_2,
            template="destruction/logs/review_created.html",
            user=archivaris,
            extra_data={"n_items": 1, "text": review_2.text},
        )

        report = create_audittrail_report(destruction_list)
        html_report = document_fromstring(report)

        self.assertEqual(4, len(html_report.find_class("log-item")))

        # The second review should not have this tag, because the review text was empty
        self.assertEqual(1, len(html_report.find_class("log-item__review-text")))
        self.assertIn("This is a comment for the author.", report)
        self.assertEqual(1, len(html_report.find_class("log-item__author-comment")))
        self.assertIn("This is a comment for the reviewer.", report)

    def test_number_of_deleted_bytes(self):
        destruction_list = DestructionListFactory.create()
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
                "verantwoordelijke_organisatie": "Nicer organisation",
                "resultaat": {
                    "resultaattype": {
                        "omschrijving": "Nicer result type",
                        "archiefactietermijn": "40 days",
                    }
                },
                "relevante_andere_zaken": [{"url": "http://some.zaak"}],
                "bytes_removed_documents": 10,
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
                "bytes_removed_documents": 20,
            },
        )
        archivaris = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=archivaris,
            text="What a magnificent list!",
        )

        report_data, deleted_bytes = get_destruction_report_data(destruction_list)

        self.assertEqual(deleted_bytes, 30)
