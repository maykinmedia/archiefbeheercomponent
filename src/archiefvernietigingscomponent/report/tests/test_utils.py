from unittest.mock import patch

from django.test import TestCase, override_settings

from freezegun import freeze_time

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

        report_data = get_destruction_report_data(destruction_list)

        self.assertEqual(1, len(report_data))

        zaak_data = report_data[0]

        self.assertNotIn("omschrijving", zaak_data)
        self.assertNotIn("opmerkingen", zaak_data)

    @patch(
        "archiefvernietigingscomponent.report.utils.get_vernietigings_categorie_selectielijst",
        return_value="1",
    )
    @patch(
        "archiefvernietigingscomponent.report.utils.get_zaaktype",
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

        report_data = get_destruction_report_data(destruction_list)

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
        "archiefvernietigingscomponent.report.utils.get_vernietigings_categorie_selectielijst",
        return_value="1",
    )
    @patch(
        "archiefvernietigingscomponent.report.utils.get_zaaktype",
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
            },
        )

        report_data = get_destruction_report_data(destruction_list)

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
        "archiefvernietigingscomponent.report.utils.get_vernietigings_categorie_selectielijst",
        return_value="1",
    )
    @patch(
        "archiefvernietigingscomponent.report.utils.get_zaaktype",
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

        report_data = get_destruction_report_data(destruction_list)

        self.assertEqual(1, len(report_data))

        self.assertEqual("ZAAK-2", report_data[0]["identificatie"])
