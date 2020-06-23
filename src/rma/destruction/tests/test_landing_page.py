"""
Test the various role landing pages.
"""
from django.urls import reverse

from django_webtest import WebTest

from rma.accounts.tests.factories import UserFactory
from rma.notifications.tests.factories import NotificationFactory


class RecordManagerTests(WebTest):
    """
    Test the role that can start destruction list processes.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(role__can_start_destruction=True)

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
        NotificationFactory.create(message="bar!", destruction_list__name="dl 2")

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
