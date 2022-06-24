import io
import zipfile

from django.core.files.base import ContentFile
from django.urls import reverse

from django_webtest import WebTest
from furl import furl
from privates.test import temp_private_root

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.constants import RoleTypeChoices
from archiefbeheercomponent.report.tests.factories import DestructionReportFactory

from .factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
    DestructionListReviewFactory,
)


@temp_private_root()
class DownloadReviewersDocumentsTests(WebTest):
    @classmethod
    def setUpTestData(cls):
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        archivist = UserFactory.create(
            role__type=RoleTypeChoices.archivist,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )

        destruction_list = DestructionListFactory.create()
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=process_owner
        )
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=archivist
        )

        uploaded_file_1 = ContentFile(
            content="Test document content", name="test_process_owner.pdf"
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            author=process_owner,
            additional_document=uploaded_file_1,
        )

        uploaded_file_2 = ContentFile(
            content="Another test document content", name="test_archivist.pdf"
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            author=archivist,
            additional_document=uploaded_file_2,
        )
        DestructionReportFactory.create(
            destruction_list=destruction_list, process_owner=process_owner
        )

        cls.process_owner = process_owner
        cls.archivist = archivist
        cls.destruction_list = destruction_list

    def test_process_owner_can_download_sees_download_docs_link(self):
        reviewer_list_page = furl(reverse("destruction:reviewer-list"))
        reviewer_list_page.args["reviewed"] = "reviewed"
        reviewer_list_page = self.app.get(
            reviewer_list_page.url, user=self.process_owner
        )

        self.assertEqual(200, reviewer_list_page.status_code)

        download_page = furl(
            reverse(
                "destruction:download-reviewer-documents",
                args=[self.destruction_list.pk],
            ),
            host="testserver",
            scheme="http",
        )
        link_node = reviewer_list_page.html.find("a", attrs={"href": download_page.url})

        self.assertIsNotNone(link_node)

    def test_process_owner_other_list_cant_download(self):
        another_process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=False,
        )

        self.client.force_login(another_process_owner)
        response = self.client.get(
            reverse(
                "destruction:download-reviewer-documents",
                args=[self.destruction_list.pk],
            )
        )

        self.assertEqual(403, response.status_code)

    def test_functioneel_beheerder_can_download(self):
        functional_admin = UserFactory.create(
            role__type=RoleTypeChoices.functional_admin,
            role__can_start_destruction=True,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )

        self.client.force_login(functional_admin)
        response = self.client.get(
            reverse(
                "destruction:download-reviewer-documents",
                args=[self.destruction_list.pk],
            )
        )

        self.assertEqual(200, response.status_code)

    def test_no_additional_documents_no_tag_in_template(self):
        # If there are no documents to download, the process owner should see no
        # link to download additional documents
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )

        destruction_list = DestructionListFactory.create()
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=process_owner
        )

        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            author=process_owner,
        )

        DestructionReportFactory.create(
            destruction_list=destruction_list, process_owner=process_owner
        )

        reviewer_list_page = furl(reverse("destruction:reviewer-list"))
        reviewer_list_page.args["reviewed"] = "reviewed"
        list_page = self.app.get(reviewer_list_page.url, user=process_owner)

        self.assertEqual(200, list_page.status_code)

        download_page = furl(
            reverse(
                "destruction:download-reviewer-documents", args=[destruction_list.pk]
            ),
            host="testserver",
            scheme="http",
        )
        link_node = list_page.html.find("a", attrs={"href": download_page.url})

        self.assertIsNone(link_node)

    def test_can_download_documents_as_zip(self):
        self.client.force_login(self.process_owner)
        response = self.client.get(
            reverse(
                "destruction:download-reviewer-documents",
                args=[self.destruction_list.pk],
            )
        )

        self.assertEqual(200, response.status_code)

        content = list(response.streaming_content)[0]

        with zipfile.ZipFile(io.BytesIO(content), "r") as file:
            names_list = file.namelist()

        self.assertEqual(2, len(names_list))
        self.assertIn("test_archivist.pdf", names_list)
        self.assertIn("test_process_owner.pdf", names_list)

    def test_404_if_no_additional_documents(self):
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )

        destruction_list = DestructionListFactory.create()
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=process_owner
        )
        DestructionListReviewFactory.create(
            destruction_list=destruction_list,
            author=process_owner,
        )

        self.client.force_login(process_owner)
        response = self.client.get(
            reverse(
                "destruction:download-reviewer-documents",
                args=[destruction_list.pk],
            )
        )

        self.assertEqual(404, response.status_code)
