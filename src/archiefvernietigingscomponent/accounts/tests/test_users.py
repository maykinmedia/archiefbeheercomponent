from django.urls import reverse

from django_webtest import WebTest

from archiefvernietigingscomponent.accounts.models import User
from archiefvernietigingscomponent.accounts.tests.factories import UserFactory


class CreateNewUser(WebTest):
    def test_can_create_new_user(self):
        user_1 = UserFactory.create(is_staff=True, is_superuser=True)
        response = self.app.get(reverse("admin:accounts_user_add"), user=user_1)
        form = response.form
        form["username"] = "test-new-user"
        form["password1"] = "t3stP4ssword"
        form["password2"] = "t3stP4ssword"

        response_submission = form.submit()

        self.assertEqual(302, response_submission.status_code)
        self.assertEqual(2, User.objects.all().count())
