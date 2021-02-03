from django.test import TestCase, override_settings
from django.urls import reverse

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory


class StartPageTests(TestCase):
    """
    Test the start page of the demo
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(role__can_start_destruction=True)

    def test_start_page_if_not_logged_in(self):
        response = self.client.get(reverse("entry"))

        self.assertEqual(200, response.status_code)
        self.assertEqual("demo/index.html", response.templates[0].name)
        self.assertEqual("demo/master.html", response.templates[1].name)

    @override_settings(AVC_DEMO_MODE=True)
    def test_start_page_with_demo_details_if_demo_mode(self):
        response = self.client.get(reverse("entry"))

        self.assertEqual(200, response.status_code)
        self.assertIn(b"demo mode", response.content)
        self.assertIn(b"Tutorial", response.content)

    @override_settings(AVC_DEMO_MODE=False)
    def test_start_page_without_demo_details_if_no_demo_mode(self):
        response = self.client.get(reverse("entry"))

        self.assertEqual(200, response.status_code)
        self.assertNotIn(b"demo mode", response.content)
        self.assertNotIn(b"Tutorial", response.content)
