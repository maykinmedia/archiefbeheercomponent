from django.core.exceptions import ValidationError
from django.test import TestCase

from archiefbeheercomponent.accounts.tests.factories import RoleFactory
from archiefbeheercomponent.constants import RoleTypeChoices


class RoleTests(TestCase):
    def test_create_record_manager_with_correct_permissions(self):
        role = RoleFactory.create(
            type=RoleTypeChoices.record_manager,
            can_start_destruction=True,
            can_view_case_details=True,
        )

        role.clean()  # Shouldn't raise exceptions

    def test_create_record_manager_with_insufficient_permissions(self):
        role = RoleFactory.create(
            type=RoleTypeChoices.record_manager,
            can_start_destruction=False,
            can_view_case_details=True,
        )

        with self.assertRaises(ValidationError):
            role.clean()

    def test_create_process_owner_with_correct_permissions(self):
        role = RoleFactory.create(
            type=RoleTypeChoices.process_owner,
            can_review_destruction=True,
            can_view_case_details=True,
        )

        role.clean()  # Shouldn't raise exceptions

    def test_create_process_owner_with_insufficient_permissions(self):
        role = RoleFactory.create(
            type=RoleTypeChoices.process_owner,
            can_review_destruction=True,
            can_view_case_details=False,
        )

        with self.assertRaises(ValidationError):
            role.clean()

    def test_create_archivist_with_correct_permissions(self):
        role = RoleFactory.create(
            type=RoleTypeChoices.archivist, can_review_destruction=True,
        )

        role.clean()  # Shouldn't raise exceptions

    def test_create_archivist_with_insufficient_permissions(self):
        role = RoleFactory.create(
            type=RoleTypeChoices.record_manager, can_review_destruction=False,
        )

        with self.assertRaises(ValidationError):
            role.clean()

    def test_create_functional_admin_with_correct_permissions(self):
        role = RoleFactory.create(
            type=RoleTypeChoices.functional_admin,
            can_review_destruction=True,
            can_start_destruction=True,
            can_view_case_details=True,
        )

        role.clean()  # Shouldn't raise exceptions

    def test_create_functional_admin_with_insufficient_permissions(self):
        role = RoleFactory.create(
            type=RoleTypeChoices.functional_admin,
            can_review_destruction=True,
            can_view_case_details=False,
            can_start_destruction=True,
        )

        with self.assertRaises(ValidationError):
            role.clean()

    def test_create_other_role_without_permissions(self):
        role = RoleFactory.create(
            type=RoleTypeChoices.other,
            can_review_destruction=False,
            can_start_destruction=False,
            can_view_case_details=False,
        )

        role.clean()  # Shouldn't raise exceptions
