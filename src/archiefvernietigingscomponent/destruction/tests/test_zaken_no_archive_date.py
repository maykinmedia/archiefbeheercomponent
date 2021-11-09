from django.test import TestCase
from django.urls import reverse

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory


class ZakenWithoutArchiveDateViewTests(TestCase):

    def test_cant_access_without_can_start_destruction(self):
        user = UserFactory(role__can_start_destruction=False)
        self.client.force_login(user)

        response = self.client.get(reverse("destruction:zaken-without-archive-date"))

        self.assertEqual(403, response.status_code)

    def test_can_access_with_can_start_destruction(self):
        user = UserFactory(role__can_start_destruction=True)
        self.client.force_login(user)

        response = self.client.get(reverse("destruction:zaken-without-archive-date"))

        self.assertEqual(200, response.status_code)
