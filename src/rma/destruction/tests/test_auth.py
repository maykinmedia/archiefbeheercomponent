from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from rma.accounts.tests.factories import UserFactory


class AuthCheckMixin:
    def assertLoginRequired(self, url):
        response = self.client.get(url)

        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={url}")

    def assertHasPermission(self, url, user):
        self.client.force_login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.client.logout()

    def assertHasNoPermission(self, url, user):
        self.client.force_login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

        self.client.logout()


class AuthTests(AuthCheckMixin, TestCase):
    def test_record_manager_landing_page(self):
        url = reverse("destruction:record-manager-list")
        record_manager = UserFactory.create(role__can_start_destruction=True)
        other_user = UserFactory.create(role__can_start_destruction=False)

        self.assertLoginRequired(url)
        self.assertHasPermission(url, record_manager)
        self.assertHasNoPermission(url, other_user)

    def test_reviewer_landing_page(self):
        url = reverse("destruction:reviewer-list")
        reviewer = UserFactory.create(role__can_review_destruction=True)
        other_user = UserFactory.create(role__can_review_destruction=False)

        self.assertLoginRequired(url)
        self.assertHasPermission(url, reviewer)
        self.assertHasNoPermission(url, other_user)
