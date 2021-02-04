from django.test import TestCase, override_settings
from django.urls import reverse

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory


class StartPageTests(TestCase):
    """
    Test the start page of the demo
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

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


@override_settings(AVC_DEMO_MODE=True)
class DemoViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.functioneel_beheer = UserFactory.create(
            username="demo-functioneel-beheer",
            role__can_start_destruction=True,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        cls.process_eigenaar = UserFactory.create(
            username="demo-process-eigenaar",
            role__can_start_destruction=False,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        cls.user = UserFactory.create(username="hello")

    @override_settings(AVC_DEMO_MODE=False)
    def test_no_demo_mode(self):
        response = self.client.get(
            reverse("demo-login", args=[self.functioneel_beheer.pk])
        )

        self.assertEqual(403, response.status_code)

    def test_demo_mode_functioneel_beheer(self):
        response = self.client.get(
            reverse("demo-login", args=[self.functioneel_beheer.pk]), follow=True
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            reverse("destruction:record-manager-list"), response.request["PATH_INFO"]
        )

    def test_demo_mode_process_eigenaar(self):
        response = self.client.get(
            reverse("demo-login", args=[self.process_eigenaar.pk]), follow=True
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            reverse("destruction:reviewer-list"), response.request["PATH_INFO"]
        )

    def test_demo_mode_normal_user(self):
        response = self.client.get(
            reverse("demo-login", args=[self.user.pk]), follow=True
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.request["PATH_INFO"], reverse("entry"))
