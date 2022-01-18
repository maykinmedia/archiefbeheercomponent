from django.test import TestCase

from ...constants import ReviewStatus
from ..factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
    DestructionListReviewFactory,
)


class NextAssigneeTests(TestCase):
    def create_list_with_assignees(self):
        destruction_list = DestructionListFactory.create()
        assignees = DestructionListAssigneeFactory.create_batch(
            2, destruction_list=destruction_list
        )
        return destruction_list, assignees

    def test_after_first_approve_review(self):
        destruction_list, assignees = self.create_list_with_assignees()
        review = DestructionListReviewFactory.create(
            status=ReviewStatus.approved,
            author=assignees[0].assignee,
            destruction_list=destruction_list,
        )

        next_assignee = destruction_list.next_assignee(review)

        self.assertEqual(next_assignee, assignees[1].assignee)

    def test_after_last_approve_review(self):
        destruction_list, assignees = self.create_list_with_assignees()
        review = DestructionListReviewFactory.create(
            status=ReviewStatus.approved,
            author=assignees[1].assignee,
            destruction_list=destruction_list,
        )

        next_assignee = destruction_list.next_assignee(review)

        self.assertEqual(next_assignee, None)

    def test_after_change_review(self):
        destruction_list, assignees = self.create_list_with_assignees()
        review = DestructionListReviewFactory.create(
            status=ReviewStatus.changes_requested,
            author=assignees[0].assignee,
            destruction_list=destruction_list,
        )

        next_assignee = destruction_list.next_assignee(review)

        self.assertEqual(next_assignee, destruction_list.author)

    def test_after_author(self):
        destruction_list, assignees = self.create_list_with_assignees()
        destruction_list.assignee = destruction_list.author
        destruction_list.save()

        next_assignee = destruction_list.next_assignee()

        self.assertEqual(next_assignee, assignees[0].assignee)

    def test_first_assignee(self):
        destruction_list, assignees = self.create_list_with_assignees()

        next_assignee = destruction_list.next_assignee()

        self.assertEqual(next_assignee, assignees[0].assignee)
