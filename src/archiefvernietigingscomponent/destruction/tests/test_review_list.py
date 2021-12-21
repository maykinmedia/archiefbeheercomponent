from unittest.mock import patch

from django.urls import reverse

from django_webtest import WebTest

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory
from archiefvernietigingscomponent.report.tests.factories import (
    DestructionReportFactory,
)

from ..constants import ReviewerDisplay
from ..models import ArchiveConfig
from .factories import DestructionListFactory, DestructionListReviewFactory


@patch(
    "archiefvernietigingscomponent.destruction.views.reviewer.ArchiveConfig.get_solo"
)
class DownloadButtonInReviewerViewTests(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(role__can_review_destruction=True)

        destruction_list = DestructionListFactory.create()
        DestructionListReviewFactory.create(
            destruction_list=destruction_list, author=cls.user
        )
        DestructionReportFactory.create(
            destruction_list=destruction_list, process_owner=cls.user
        )

    def test_no_download_button_if_download_not_configured(self, m_archive_config):
        m_archive_config.return_value = ArchiveConfig(
            destruction_report_downloadable=False
        )

        response = self.app.get(
            reverse("destruction:reviewer-list"),
            {"reviewed": ReviewerDisplay.reviewed},
            user=self.user,
        )

        self.assertEqual(200, response.status_code)
        download_nodes = response.html.find_all(
            class_="destruction-list-preview__download-report"
        )
        self.assertEqual(0, len(download_nodes))

    def test_download_button_present_if_download_configured(self, m_archive_config):
        m_archive_config.return_value = ArchiveConfig(
            destruction_report_downloadable=True
        )

        response = self.app.get(
            reverse("destruction:reviewer-list"),
            {"reviewed": ReviewerDisplay.reviewed},
            user=self.user,
        )

        self.assertEqual(200, response.status_code)
        download_nodes = response.html.find_all(
            class_="destruction-list-preview__download-report"
        )
        self.assertEqual(1, len(download_nodes))
