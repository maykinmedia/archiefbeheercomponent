from django.conf import settings
from django.test import TestCase
from django.urls import reverse_lazy

from rma.accounts.tests.factories import UserFactory


class RecordManagerAuthTests(TestCase):
    url = reverse_lazy("destruction:record-manager-list")

    def test_has_permission(self):
        user = UserFactory.create(role__can_start_destruction=True)
        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_no_permission(self):
        user = UserFactory.create(role__can_start_destruction=False)
        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_not_auth(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(str(settings.LOGIN_URL)))
