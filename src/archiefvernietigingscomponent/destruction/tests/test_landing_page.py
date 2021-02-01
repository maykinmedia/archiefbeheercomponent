"""
Test the various role landing pages.
"""
from django.test import override_settings
from django.urls import reverse

from django_webtest import WebTest

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory
from archiefvernietigingscomponent.notifications.tests.factories import (
    NotificationFactory,
)

from ..constants import ReviewerDisplay
from .factories import DestructionListFactory, DestructionListReviewFactory


class RecordManagerTests(WebTest):
    """
    Test the role that can start destruction list processes.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(role__can_start_destruction=True)

    def test_start_page_if_not_logged_in(self):
        response = self.app.get(reverse("entry"))

        self.assertEqual(200, response.status_code)
        self.assertEqual("demo/index.html", response.template[0].name)
        self.assertEqual("demo/master.html", response.template[1].name)

    @override_settings(AVC_DEMO_MODE=True)
    def test_start_page_with_demo_details_if_demo_mode(self):
        response = self.app.get(reverse("entry"))

        self.assertEqual(200, response.status_code)
        self.assertIn("demo mode", response.text)

    @override_settings(AVC_DEMO_MODE=False)
    def test_start_page_without_demo_details_if_no_demo_mode(self):
        response = self.app.get(reverse("entry"))

        self.assertEqual(200, response.status_code)
        self.assertNotIn("demo mode", response.text)

    def test_redirect(self):
        response = self.app.get(reverse("entry"), user=self.user).follow()

        self.assertEqual(
            response.request.path, reverse("destruction:record-manager-list")
        )

    def test_notifications_rendered(self):
        # notification for current user
        NotificationFactory.create(
            user=self.user, message="foo!", destruction_list__name="dl 1"
        )
        # notification for other user
        NotificationFactory.create(
            message="bar!", destruction_list__name="dl 2", user__role__name="other role"
        )

        response = self.app.get(
            reverse("destruction:record-manager-list"), user=self.user
        )

        self.assertTemplateUsed(response, "notifications/includes/notifications.html")
        self.assertContains(response, "foo!")
        self.assertNotContains(response, "bar!")

    def test_notification_list_truncated(self):
        for i in range(0, 11):
            NotificationFactory.create(
                user=self.user,
                message=f"notification {i}",
                destruction_list__name=f"dl {i}",
                destruction_list__author__role__name=f"role {i}",
            )

        response = self.app.get(
            reverse("destruction:record-manager-list"), user=self.user
        )

        for i in range(10, 0, -1):
            msg = f"notification {i}"
            with self.subTest(message=msg):
                self.assertContains(response, msg)

        msg = "notification 0"
        with self.subTest(message=msg):
            self.assertNotContains(response, msg)


class ReviewerTests(WebTest):
    """
    Test the role that can review destruction list processes.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(role__can_review_destruction=True)

        cls.list_to_review = DestructionListFactory.create(
            assignee=cls.user, name="list to review"
        )
        cls.list_reviewed = DestructionListFactory.create(name="list reviewed")
        DestructionListReviewFactory.create(
            destruction_list=cls.list_reviewed, author=cls.user
        )
        cls.list_extra = DestructionListFactory.create(
            author=cls.user, name="list extra"
        )

    def setUp(self) -> None:
        super().setUp()

        self.app.set_user(self.user)
        self.url = reverse("destruction:reviewer-list")

    def test_redirect(self):
        response = self.app.get(reverse("entry")).follow()

        self.assertEqual(response.request.path, self.url)

    def test_filter_to_review(self):
        response = self.app.get(self.url, {"reviewed": ReviewerDisplay.to_review})

        self.assertEqual(response.status_code, 200)

        destruction_lists = response.html.find_all(class_="destruction-list-preview")
        self.assertEqual(len(destruction_lists), 1)

        destruction_list = destruction_lists[0]
        self.assertTrue(self.list_to_review.name in destruction_list.get_text())

        for destr_list in [self.list_reviewed, self.list_extra]:
            self.assertFalse(destr_list.name in destruction_list.get_text())

    def test_filter_reviewed(self):
        response = self.app.get(self.url, {"reviewed": ReviewerDisplay.reviewed})

        self.assertEqual(response.status_code, 200)

        destruction_lists = response.html.find_all(class_="destruction-list-preview")
        self.assertEqual(len(destruction_lists), 1)

        destruction_list = destruction_lists[0]
        self.assertTrue(self.list_reviewed.name in destruction_list.get_text())

        for destr_list in [self.list_to_review, self.list_extra]:
            self.assertFalse(destr_list.name in destruction_list.get_text())

    def test_filter_all(self):
        response = self.app.get(self.url, {"reviewed": ReviewerDisplay.all})

        self.assertEqual(response.status_code, 200)

        destruction_lists = response.html.find_all(class_="destruction-list-preview")
        self.assertEqual(len(destruction_lists), 2)

        for destr_list in [self.list_to_review, self.list_reviewed]:
            self.assertContains(response, destr_list.name)

        self.assertNotContains(response, self.list_extra.name)

    def test_filter_default(self):
        response_default = self.app.get(self.url)
        response_to_review = self.app.get(
            self.url, {"reviewed": ReviewerDisplay.to_review}
        )

        self.assertEqual(response_default.body, response_to_review.body)
