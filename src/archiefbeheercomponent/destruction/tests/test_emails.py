from django.core import mail
from django.test import TestCase

from archiefbeheercomponent.accounts.tests.factories import RoleFactory, UserFactory
from archiefbeheercomponent.destruction.tests.factories import (
    DestructionListAssigneeFactory,
    DestructionListFactory,
)
from archiefbeheercomponent.emails.constants import EmailTypeChoices
from archiefbeheercomponent.emails.tests.factories import AutomaticEmailFactory


class AutomaticEmailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        AutomaticEmailFactory.create(
            type=EmailTypeChoices.review_required,
            body="Review is required!",
            subject="Review",
        )
        AutomaticEmailFactory.create(
            type=EmailTypeChoices.changes_required,
            body="Changes are required!",
            subject="Changes",
        )

        record_manager = RoleFactory.create(record_manager=True)
        process_owner = RoleFactory.create(process_owner=True)

        user_author = UserFactory.create(
            role=record_manager, email="author@example.com"
        )
        user_reviewer = UserFactory.create(
            role=process_owner, email="reviewer@example.com"
        )

        destruction_list = DestructionListFactory.create(author=user_author)
        DestructionListAssigneeFactory.create(
            destruction_list=destruction_list, assignee=user_reviewer
        )

        cls.destruction_list = destruction_list
        cls.user_author = user_author
        cls.user_reviewer = user_reviewer

    def test_reviewer_assigned(self):
        # Assigning the reviewer sends the reviewer an email
        self.destruction_list.assign(self.user_reviewer)
        self.destruction_list.save()

        self.assertEqual(1, len(mail.outbox))

        sent_mail = mail.outbox[0]

        self.assertEqual(["reviewer@example.com"], sent_mail.to)
        self.assertEqual("Review is required!", sent_mail.body)
        self.assertEqual("Review", sent_mail.subject)

    def test_author_assigned(self):
        # Assigning the author sends them an email
        self.destruction_list.assign(self.user_author)
        self.destruction_list.save()

        self.assertEqual(1, len(mail.outbox))

        sent_mail = mail.outbox[0]

        self.assertEqual(["author@example.com"], sent_mail.to)
        self.assertEqual("Changes are required!", sent_mail.body)
        self.assertEqual("Changes", sent_mail.subject)
