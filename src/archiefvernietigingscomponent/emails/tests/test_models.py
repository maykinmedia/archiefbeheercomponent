from django.core import mail
from django.test import TestCase

from archiefvernietigingscomponent.emails.tests.factories import AutomaticEmailFactory
from archiefvernietigingscomponent.report.tests.factories import (
    DestructionReportFactory,
)


class AutomaticEmailTest(TestCase):
    def test_email_body_and_subject(self):
        email = AutomaticEmailFactory(
            body="This is a test text", subject="This is a test subject"
        )
        email.send(recipient="test@example.com")

        self.assertEqual(1, len(mail.outbox))

        sent_mail = mail.outbox[0]

        self.assertEqual("This is a test text", sent_mail.body)
        self.assertEqual("This is a test subject", sent_mail.subject)

    def test_send_email_with_attached_report(self):
        report = DestructionReportFactory.create()
        email = AutomaticEmailFactory(
            body="This is a test text", subject="This is a test subject"
        )

        email.send(recipient="test@example.com", report=report)

        self.assertEqual(1, len(mail.outbox))

        sent_mail = mail.outbox[0]

        self.assertEqual("This is a test text", sent_mail.body)
        self.assertEqual("This is a test subject", sent_mail.subject)
        self.assertEqual(1, len(sent_mail.attachments))
