from django.test import TestCase

from archiefvernietigingscomponent.accounts.tests.factories import UserFactory
from archiefvernietigingscomponent.constants import RoleTypeChoices
from archiefvernietigingscomponent.destruction.constants import RecordManagerDisplay
from archiefvernietigingscomponent.destruction.filters import RecordManagerListFilter
from archiefvernietigingscomponent.destruction.models import DestructionList
from archiefvernietigingscomponent.destruction.tests.factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
)


class RecordManagerFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.record_manager = UserFactory(
            role__can_start_destruction=True, role__type=RoleTypeChoices.record_manager
        )
        cls.process_owner = UserFactory(
            role__can_review_destruction=True, role__type=RoleTypeChoices.process_owner
        )

        # List 1: In progress
        cls.dl_in_progress = DestructionListFactory.create(author=cls.record_manager)
        assignee = DestructionListAssigneeFactory.create(
            assignee=cls.process_owner, destruction_list=cls.dl_in_progress, order=1
        )
        cls.dl_in_progress.assignee = assignee.assignee
        cls.dl_in_progress.save()

        # List 2: Changes requested
        cls.dl_changes_required = DestructionListFactory.create(
            author=cls.record_manager
        )
        assignee = DestructionListAssigneeFactory.create(
            assignee=cls.record_manager, destruction_list=cls.dl_changes_required
        )
        cls.dl_changes_required.assignee = assignee.assignee
        cls.dl_changes_required.save()

        # List 3: Rejected
        cls.dl_rejected = DestructionListFactory.create(author=cls.record_manager)
        assignee = DestructionListAssigneeFactory.create(
            assignee=cls.record_manager, destruction_list=cls.dl_rejected
        )
        cls.dl_rejected.assignee = assignee.assignee
        cls.dl_rejected.save()

        # List 4: Approved
        cls.dl_approved = DestructionListFactory.create(author=cls.record_manager)
        cls.dl_approved.assignee = None
        cls.dl_approved.save()

        # List 5: Complete
        cls.dl_complete = DestructionListFactory.create(author=cls.record_manager)
        cls.dl_complete.process()
        cls.dl_complete.save()
        cls.dl_complete.complete()
        cls.dl_complete.save()

    def test_all_lists(self):
        filter = RecordManagerListFilter(data=None)
        qs = DestructionList.objects.all()

        filtered_qs = filter.filter_list_status(
            qs, name="", value=RecordManagerDisplay.all
        )

        self.assertEqual(5, filtered_qs.count())

    def test_in_progress(self):
        filter = RecordManagerListFilter(data=None)
        qs = DestructionList.objects.all()

        filtered_qs = filter.filter_list_status(
            qs, name="", value=RecordManagerDisplay.in_progress
        )

        self.assertEqual(2, filtered_qs.count())

        self.assertTrue(filtered_qs.filter(pk=self.dl_in_progress.pk).exists())
        self.assertTrue(filtered_qs.filter(pk=self.dl_approved.pk).exists())

    def test_action_required(self):
        filter = RecordManagerListFilter(data=None)
        qs = DestructionList.objects.all()

        filtered_qs = filter.filter_list_status(
            qs, name="", value=RecordManagerDisplay.action_required
        )

        self.assertEqual(2, filtered_qs.count())

        self.assertTrue(filtered_qs.filter(pk=self.dl_changes_required.pk).exists())
        self.assertTrue(filtered_qs.filter(pk=self.dl_rejected.pk).exists())

    def test_complete(self):
        filter = RecordManagerListFilter(data=None)
        qs = DestructionList.objects.all()

        filtered_qs = filter.filter_list_status(
            qs, name="", value=RecordManagerDisplay.completed
        )

        self.assertEqual(1, filtered_qs.count())

        self.assertTrue(filtered_qs.filter(pk=self.dl_complete.pk).exists())
