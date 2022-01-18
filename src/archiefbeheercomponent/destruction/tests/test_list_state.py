from django.test import TestCase

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.constants import RoleTypeChoices
from archiefbeheercomponent.destruction.constants import ReviewStatus
from archiefbeheercomponent.destruction.tests.factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
    DestructionListReviewFactory,
)


class ListStateTest(TestCase):
    def test_state_after_creation(self):
        record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.record_manager
        )
        process_owner = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.process_owner
        )

        destruction_list = DestructionListFactory.create(author=record_manager)

        assignee = DestructionListAssigneeFactory.create(
            assignee=process_owner, destruction_list=destruction_list, order=1
        )
        destruction_list.assignee = assignee.assignee
        destruction_list.save()

        list_state = destruction_list.list_state()

        self.assertEqual("in_progress", list_state.value)
        self.assertEqual(1, destruction_list.total_reviewers())
        self.assertEqual(0, destruction_list.completed_reviewers())

    def test_state_after_first_review(self):
        record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.record_manager
        )
        process_owner = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.process_owner
        )
        archivist = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.archivist
        )

        destruction_list = DestructionListFactory.create(author=record_manager)

        DestructionListAssigneeFactory.create(
            assignee=process_owner, destruction_list=destruction_list, order=1
        )
        assignee = DestructionListAssigneeFactory.create(
            assignee=archivist, destruction_list=destruction_list, order=2
        )

        DestructionListReviewFactory.create(
            author=process_owner,
            status=ReviewStatus.approved,
            destruction_list=destruction_list,
        )

        destruction_list.assignee = assignee.assignee
        destruction_list.save()

        list_state = destruction_list.list_state()

        self.assertEqual("in_progress", list_state.value)
        self.assertEqual(2, destruction_list.total_reviewers())
        self.assertEqual(1, destruction_list.completed_reviewers())

    def test_state_after_last_review(self):
        record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.record_manager
        )
        destruction_list = DestructionListFactory.create(author=record_manager)

        destruction_list.assignee = None
        destruction_list.save()

        list_state = destruction_list.list_state()

        self.assertEqual("approved", list_state.value)

    def test_state_after_rejection(self):
        record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.record_manager
        )
        archivist = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.archivist
        )

        destruction_list = DestructionListFactory.create(author=record_manager)

        DestructionListReviewFactory.create(
            author=archivist,
            status=ReviewStatus.rejected,
            destruction_list=destruction_list,
        )
        destruction_list.assignee = record_manager
        destruction_list.save()

        list_state = destruction_list.list_state()

        self.assertEqual("rejected", list_state.value)

    def test_state_after_changes_requested(self):
        record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.record_manager
        )
        process_owner = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.process_owner
        )
        archivist = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.archivist
        )

        destruction_list = DestructionListFactory.create(author=record_manager)

        DestructionListAssigneeFactory.create(
            assignee=process_owner, destruction_list=destruction_list, order=1
        )
        DestructionListAssigneeFactory.create(
            assignee=archivist, destruction_list=destruction_list, order=2
        )

        DestructionListReviewFactory.create(
            author=process_owner,
            status=ReviewStatus.changes_requested,
            destruction_list=destruction_list,
        )

        destruction_list.assignee = record_manager
        destruction_list.save()

        list_state = destruction_list.list_state()

        self.assertEqual("changes_requested", list_state.value)
        self.assertEqual(2, destruction_list.total_reviewers())
        self.assertEqual(0, destruction_list.completed_reviewers())

    def test_state_after_destruction(self):
        process_owner = UserFactory.create(
            role__type=RoleTypeChoices.process_owner,
            role__can_review_destruction=True,
            role__can_view_case_details=True,
        )
        destruction_list = DestructionListFactory.create(name="Summer List",)
        DestructionListReviewFactory.create(
            author=process_owner,
            status=ReviewStatus.approved,
            destruction_list=destruction_list,
        )

        destruction_list.process()
        destruction_list.complete()
        destruction_list.save()

        list_state = destruction_list.list_state()

        self.assertEqual("finished", list_state.value)
