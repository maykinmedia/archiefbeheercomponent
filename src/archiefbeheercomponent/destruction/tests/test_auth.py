from django.conf import settings
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from archiefbeheercomponent.accounts.tests.factories import UserFactory

from .factories import DestructionListAssigneeFactory, DestructionListFactory


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


class LandingTests(AuthCheckMixin, TestCase):
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


class FetchListItemsTests(AuthCheckMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.destruction_list = DestructionListFactory.create()

    def setUp(self) -> None:
        super().setUp()

        self.url = reverse_lazy(
            "destruction:fetch-list-items", args=[self.destruction_list.id]
        )

    def test_unauthorized(self):
        self.assertLoginRequired(self.url)

    def test_without_role(self):
        user = UserFactory.create(role=None)
        self.assertHasNoPermission(self.url, user)

    def test_author(self):
        self.assertHasPermission(self.url, self.destruction_list.author)

    def test_assignee(self):
        assignee = DestructionListAssigneeFactory.create(
            destruction_list=self.destruction_list
        )
        self.assertHasPermission(self.url, assignee.assignee)

    def test_with_role_no_assignee_no_author(self):
        user = UserFactory.create()
        self.assertHasNoPermission(self.url, user)


class DestructionListDetailTests(AuthCheckMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.destruction_list = DestructionListFactory.create()

    def setUp(self) -> None:
        super().setUp()

        self.url = reverse_lazy(
            "destruction:record-manager-detail", args=[self.destruction_list.id]
        )

    def test_unauthorized(self):
        self.assertLoginRequired(self.url)

    def test_author(self):
        self.assertHasPermission(self.url, self.destruction_list.author)

    def test_assignee(self):
        assignee = DestructionListAssigneeFactory.create(
            destruction_list=self.destruction_list
        )
        self.assertHasPermission(self.url, assignee.assignee)

    def test_no_assignee_no_author(self):
        user = UserFactory.create()
        self.assertHasNoPermission(self.url, user)
