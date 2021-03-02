from django.test import TestCase
from django.urls import reverse

from privates.test import temp_private_root

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory
from archiefvernietigingscomponent.constants import RoleTypeChoices
from archiefvernietigingscomponent.report.tests.factories import (
    DestructionReportFactory,
)


@temp_private_root()
class DownloadDestructionReportTests(TestCase):
    def test_non_authenticated_redirected_to_login(self):
        report = DestructionReportFactory.create()

        response = self.client.get(reverse("report:download-report", args=[report.pk]))

        self.assertEqual(302, response.status_code)
        self.assertIn(reverse("admin:login"), response.url)

    def test_archivarist_cant_access(self):
        process_owner = UserFactory.create(role__type=RoleTypeChoices.process_owner)
        archivist = UserFactory.create(role__type=RoleTypeChoices.archivist)
        report = DestructionReportFactory.create(process_owner=process_owner)

        self.client.force_login(archivist)
        response = self.client.get(reverse("report:download-report", args=[report.pk]))

        self.assertEqual(403, response.status_code)

    def test_functional_admin_can_access(self):
        process_owner = UserFactory.create(role__type=RoleTypeChoices.process_owner)
        functional_admin = UserFactory.create(
            role__type=RoleTypeChoices.functional_admin
        )
        report = DestructionReportFactory.create(process_owner=process_owner)

        self.client.force_login(functional_admin)
        response = self.client.get(reverse("report:download-report", args=[report.pk]))

        self.assertEqual(200, response.status_code)

    def test_only_assigned_process_owner_can_access(self):
        process_owner_assigned = UserFactory.create(
            role__type=RoleTypeChoices.process_owner
        )
        another_process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner
        )
        report = DestructionReportFactory.create(process_owner=process_owner_assigned)

        self.client.force_login(process_owner_assigned)
        response = self.client.get(reverse("report:download-report", args=[report.pk]))

        self.assertEqual(200, response.status_code)

        self.client.force_login(another_process_owner)
        response = self.client.get(reverse("report:download-report", args=[report.pk]))

        self.assertEqual(403, response.status_code)
