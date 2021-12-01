from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time

from archiefvernietigingscomponent.accounts.tests.factories import RoleFactory
from archiefvernietigingscomponent.destruction.models import ArchiveConfig
from archiefvernietigingscomponent.destruction.tests.factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
)


@freeze_time("2021-11-16 12:00")
class IsReviewOverdueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        config = ArchiveConfig.get_solo()
        config.days_until_reminder = 2
        config.save()

    def test_review_is_overdue(self):
        role = RoleFactory.create(can_review_destruction=True)
        destruction_list = DestructionListFactory.create()
        reviewer = DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee__role=role
        )

        destruction_list.assignee = reviewer.assignee
        destruction_list.save()
        reviewer.assigned_on = timezone.make_aware(datetime(2021, 11, 12))
        reviewer.save()

        self.assertTrue(destruction_list.is_review_overdue)

    def test_review_is_not_overdue(self):
        role = RoleFactory.create(can_review_destruction=True)
        destruction_list = DestructionListFactory.create()
        reviewer = DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee__role=role
        )

        destruction_list.assignee = reviewer.assignee
        destruction_list.save()
        reviewer.assigned_on = timezone.make_aware(datetime(2021, 11, 15))
        reviewer.save()

        self.assertFalse(destruction_list.is_review_overdue)

    def test_no_reviewer_assigned(self):
        destruction_list = DestructionListFactory.create()
        destruction_list.assignee = None
        destruction_list.save()

        self.assertFalse(destruction_list.is_review_overdue)

    def test_assignee_is_no_reviewer(self):
        role = RoleFactory.create(can_review_destruction=False)
        destruction_list = DestructionListFactory.create()
        reviewer = DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee__role=role
        )
        destruction_list.assignee = reviewer.assignee
        destruction_list.save()
        reviewer.assigned_on = timezone.make_aware(datetime(2021, 11, 12))
        reviewer.save()

        self.assertFalse(destruction_list.is_review_overdue)
