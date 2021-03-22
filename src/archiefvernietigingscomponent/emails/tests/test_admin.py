from django.urls import reverse

from django_webtest import WebTest

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory
from archiefvernietigingscomponent.emails.constants import EmailTypeChoices
from archiefvernietigingscomponent.emails.models import AutomaticEmail


class AutomaticEmailAdminTest(WebTest):
    def test_no_variables(self):
        user = UserFactory.create(is_staff=True, is_superuser=True)

        response = self.app.get(reverse("admin:emails_automaticemail_add"), user=user)

        form = response.form

        form["type"] = EmailTypeChoices.review_required
        form["body"] = "This is a test body"
        form["subject"] = "Test subject"

        response = form.submit().follow()

        self.assertEqual(200, response.status_code)

        self.assertEqual(1, AutomaticEmail.objects.count())

    def test_correct_variables(self):
        user = UserFactory.create(is_staff=True, is_superuser=True)

        response = self.app.get(reverse("admin:emails_automaticemail_add"), user=user)

        form = response.form

        form["type"] = EmailTypeChoices.review_required
        form["body"] = "This is a test body with a variable {{ municipality }}"
        form["subject"] = "Test subject"

        response = form.submit().follow()

        self.assertEqual(200, response.status_code)

        self.assertEqual(1, AutomaticEmail.objects.count())

    def test_unknown_variable(self):
        user = UserFactory.create(is_staff=True, is_superuser=True)

        response = self.app.get(reverse("admin:emails_automaticemail_add"), user=user)

        form = response.form

        form["type"] = EmailTypeChoices.review_required
        form["body"] = "This is a test body with an unknown variable {{ unknown }}"
        form["subject"] = "Test subject"

        response = form.submit()

        self.assertIn("Unknown variable used in the email body.", response.text)

        self.assertEqual(0, AutomaticEmail.objects.count())

    def test_wrong_variable(self):
        user = UserFactory.create(is_staff=True, is_superuser=True)

        response = self.app.get(reverse("admin:emails_automaticemail_add"), user=user)

        form = response.form

        form["type"] = EmailTypeChoices.review_required
        form["body"] = "This is a test body with an unknown variable {{ link_report }}"
        form["subject"] = "Test subject"

        response = form.submit()

        self.assertIn(
            "Cannot include the report link in the body of this type of email.",
            response.text,
        )

        self.assertEqual(0, AutomaticEmail.objects.count())
