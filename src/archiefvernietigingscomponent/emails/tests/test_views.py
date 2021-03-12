from django.test import TestCase
from django.urls import reverse

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory


class EmailPreferenceUpdateTest(TestCase):
    def test_wrong_user_cant_access(self):
        user_1 = UserFactory.create()
        user_2 = UserFactory.create()

        self.client.force_login(user_1)
        response = self.client.get(
            reverse("emails:email-preference-update", args=[user_2.emailpreference.pk])
        )

        self.assertEqual(403, response.status_code)

    def test_right_user_can_access(self):
        user = UserFactory.create()

        self.client.force_login(user)
        response = self.client.get(
            reverse("emails:email-preference-update", args=[user.emailpreference.pk])
        )

        self.assertEqual(200, response.status_code)
