from django.test import TestCase
from django.urls import reverse

from django_webtest import WebTest

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.constants import RoleTypeChoices


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


class EmailPreferenceLinkTest(WebTest):
    def test_link_process_owner(self):
        process_owner = UserFactory.create(
            role__can_review_destruction=True, role__type=RoleTypeChoices.process_owner
        )

        response = self.app.get(reverse("entry"), user=process_owner).follow()

        self.assertEqual(200, response.status_code)

        url_email_preferences = reverse(
            "emails:email-preference-update", args=[process_owner.emailpreference.pk]
        )

        link_present = False
        for link in response.html.find_all("a"):
            if link.attrs["href"] == url_email_preferences:
                link_present = True
                break

        self.assertTrue(link_present)

    def test_link_record_manager(self):
        record_manager = UserFactory.create(
            role__can_start_destruction=True, role__type=RoleTypeChoices.record_manager
        )

        response = self.app.get(reverse("entry"), user=record_manager).follow()

        self.assertEqual(200, response.status_code)

        url_email_preferences = reverse(
            "emails:email-preference-update", args=[record_manager.emailpreference.pk]
        )

        link_present = False
        for link in response.html.find_all("a"):
            if link.attrs["href"] == url_email_preferences:
                link_present = True
                break

        self.assertTrue(link_present)
