from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from freezegun import freeze_time
from privates.test import temp_private_root

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.constants import RoleTypeChoices
from archiefbeheercomponent.destruction.constants import ListItemStatus, ReviewStatus
from archiefbeheercomponent.destruction.models import DestructionList
from archiefbeheercomponent.destruction.tests.factories import (
    DestructionListFactory,
    DestructionListItemFactory,
    DestructionListReviewFactory,
)
from archiefbeheercomponent.report.utils import (
    create_csv_report_content,
    create_destruction_report,
    create_html_report_content,
    get_destruction_report_data,
)


@temp_private_root()
@override_settings(LANGUAGE_CODE="en")
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
class CreateReportTests(TestCase):
    @freeze_time("2021-05-05")
    def test_invalid_report_type(self, m_vcs, m_zaaktype):
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
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )

        report = create_destruction_report(destruction_list)

        self.assertEqual(process_owner, report.process_owner)
        self.assertEqual(
            "Declaration of destruction - Winter cases (2021-05-05)", report.title
        )

        self.client.force_login(process_owner)
        response = self.client.get(
            reverse("report:download-report", args=[report.pk]), data={"type": "GNE"}
        )

        self.assertEqual(400, response.status_code)

    def test_pdf_report_creation_with_process_owner(self, m_vcs, m_zaaktype):
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
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )

        report = create_destruction_report(destruction_list)

        self.client.force_login(process_owner)
        response = self.client.get(
            reverse("report:download-report", args=[report.pk]), data={"type": "pdf"}
        )

        self.assertEqual(200, response.status_code)
        self.assertGreater(len(response.content), 0)

    def test_csv_report_creation_with_process_owner(self, m_vcs, m_zaaktype):
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
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )

        report = create_destruction_report(destruction_list)

        self.client.force_login(process_owner)
        response = self.client.get(
            reverse("report:download-report", args=[report.pk]), data={"type": "csv"}
        )

        self.assertEqual(200, response.status_code)
        self.assertGreater(len(response.content), 0)

    def test_report_creation_without_process_owner(self, m_vcs, m_zaaktype):
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

        report = create_destruction_report(destruction_list)

        self.assertEqual(None, report.process_owner)

    def test_private_media_is_not_accessible(self, m_vcs, m_zaaktype):
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
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            author=process_owner,
            text="What a magnificent list!",
        )

        report = create_destruction_report(destruction_list)

        response_csv = self.client.get(report.content_csv.url)

        self.assertEqual(404, response_csv.status_code)

        response_pdf = self.client.get(report.content_pdf.url)

        self.assertEqual(404, response_pdf.status_code)

    def test_relation_between_report_and_destructionlist(self, m_vcs, m_zaaktype):
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
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            status=ReviewStatus.approved,
            text="What a magnificent list!",
        )

        report = create_destruction_report(destruction_list)

        # can't use refresh_from_db() because of django-fsm
        destruction_list = DestructionList.objects.get(id=destruction_list.id)

        self.assertEqual(1, destruction_list.destructionreport_set.count())
        self.assertEqual(report, destruction_list.destructionreport_set.get())


@override_settings(LANGUAGE_CODE="en")
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
class ContentReportTests(TestCase):
    def test_create_html_content_with_sensitive_info(self, m_vcs, m_zaaktype):
        destruction_list = DestructionListFactory.create(
            name="Winter cases",
            contains_sensitive_info=True,
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

        zaken_data, bytes_deleted = get_destruction_report_data(destruction_list)
        html_content = create_html_report_content(
            zaken_data, bytes_deleted, destruction_list.contains_sensitive_info
        )

        expected_html_nodes = [
            "<th>Unique ID</th>",
            "<th>Duration</th>",
            "<th>Destruction category Selectielijst</th>",
            "<th>Explanation</th>",
            "<th>Reaction caretaker</th>",
            "<th>Case type</th>",
            "<th>Archive action period</th>",
            "<th>Result type</th>",
            "<th>Organisation responsible</th>",
            "<th>Relations</th>",
            "<td>ZAAK-1</td>",
            "<td>366 days</td>",
            "<td>1</td>",
            "<td>Bah</td>",
            "<td></td>",
            "<td>This is a zaaktype</td>",
            "<td>40 days</td>",
            "<td>Nicer result type</td>",
            "<td>Nicer organisation</td>",
            "<td>Yes</td>",
            "10\xa0bytes of documents were deleted.",
        ]

        for node in expected_html_nodes:
            self.assertInHTML(node, html_content)

        # Check sensitive info
        self.assertNotIn("<th>Description</th>", html_content)
        self.assertNotIn("<th>Remarks SAD</th>", html_content)
        self.assertNotIn("<td>Een zaak</td>", html_content)
        self.assertNotIn("<td>What a magnificent list!</td>", html_content)

    def test_create_html_content_without_sensitive_info(self, m_vcs, m_zaaktype):
        destruction_list = DestructionListFactory.create(
            name="Winter cases",
            contains_sensitive_info=False,
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

        zaken_data, bytes_deleted = get_destruction_report_data(destruction_list)
        html_content = create_html_report_content(
            zaken_data, bytes_deleted, destruction_list.contains_sensitive_info
        )

        expected_html_nodes = [
            "<th>Unique ID</th>",
            "<th>Description</th>",
            "<th>Duration</th>",
            "<th>Destruction category Selectielijst</th>",
            "<th>Explanation</th>",
            "<th>Reaction caretaker</th>",
            "<th>Remarks SAD</th>",
            "<th>Case type</th>",
            "<th>Archive action period</th>",
            "<th>Result type</th>",
            "<th>Organisation responsible</th>",
            "<th>Relations</th>",
            "<td>Een zaak</td>",
            "<td>ZAAK-1</td>",
            "<td>What a magnificent list!</td>",
            "<td>366 days</td>",
            "<td>1</td>",
            "<td>Bah</td>",
            "<td></td>",
            "<td>This is a zaaktype</td>",
            "<td>40 days</td>",
            "<td>Nicer result type</td>",
            "<td>Nicer organisation</td>",
            "<td>Yes</td>",
        ]

        for node in expected_html_nodes:
            self.assertInHTML(node, html_content)

    def test_create_csv_content_with_sensitive_info(self, m_vcs, m_zaaktype):
        destruction_list = DestructionListFactory.create(
            name="Winter cases",
            contains_sensitive_info=True,
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

        zaken_data, bytes_deleted = get_destruction_report_data(destruction_list)
        html_content = create_csv_report_content(
            zaken_data, destruction_list.contains_sensitive_info
        )

        expected_header_row = [
            "Unique ID",
            "Duration",
            "Destruction category Selectielijst",
            "Explanation",
            "Reaction caretaker",
            "Case type",
            "Archive action period",
            "Result type",
            "Organisation responsible",
            "Relations",
        ]
        expected_zaak_row = [
            "ZAAK-1",
            "366 days",
            "1",
            "Bah",
            "",
            "This is a zaaktype",
            "40 days",
            "Nicer result type",
            "Nicer organisation",
            "Yes",
        ]

        html_content.seek(0)

        lines = [line for line in html_content.readlines()]

        self.assertEqual(2, len(lines))
        for header in expected_header_row:
            self.assertIn(header, lines[0])

        for zaak in expected_zaak_row:
            self.assertIn(zaak, lines[1])

        self.assertNotIn("Description", lines[0])
        self.assertNotIn("Remarks SAD", lines[0])
        self.assertNotIn("Een zaak", lines[1])
        self.assertNotIn("What a magnificent list!", lines[1])

    def test_create_csv_content_without_sensitive_info(self, m_vcs, m_zaaktype):
        destruction_list = DestructionListFactory.create(
            name="Winter cases",
            contains_sensitive_info=False,
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

        zaken_data, bytes_deleted = get_destruction_report_data(destruction_list)
        html_content = create_csv_report_content(
            zaken_data, destruction_list.contains_sensitive_info
        )

        html_content.seek(0)

        lines = [line for line in html_content.readlines()]

        expected_header_row = [
            "Unique ID",
            "Description",
            "Duration",
            "Destruction category Selectielijst",
            "Explanation",
            "Remarks SAD",
            "Reaction caretaker",
            "Case type",
            "Archive action period",
            "Result type",
            "Organisation responsible",
            "Relations",
        ]
        expected_zaak_row = [
            "ZAAK-1",
            "Een zaak",
            "366 days",
            "1",
            "Bah",
            "What a magnificent list!",
            "",
            "This is a zaaktype",
            "40 days",
            "Nicer result type",
            "Nicer organisation",
            "Yes",
        ]

        self.assertEqual(2, len(lines))
        for header in expected_header_row:
            self.assertIn(header, lines[0])

        for zaak in expected_zaak_row:
            self.assertIn(zaak, lines[1])
