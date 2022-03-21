from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from furl import furl
from privates.test import temp_private_root

from archiefbeheercomponent.accounts.tests.factories import UserFactory
from archiefbeheercomponent.destruction.tests.factories import DestructionListFactory
from archiefbeheercomponent.emails.constants import EmailTypeChoices
from archiefbeheercomponent.emails.models import EmailConfig
from archiefbeheercomponent.emails.tests.factories import AutomaticEmailFactory
from archiefbeheercomponent.report.constants import ReportTypeChoices
from archiefbeheercomponent.report.tests.factories import DestructionReportFactory
from archiefbeheercomponent.report.utils import get_absolute_url


@temp_private_root()
@override_settings(LANGUAGE_CODE="en")
class AutomaticEmailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(email="test@example.com")

    def test_email_body_and_subject(self):
        destruction_list = DestructionListFactory.create()
        email = AutomaticEmailFactory(
            body="This is a test text", subject="This is a test subject"
        )
        email.send(recipient=self.user, destruction_list=destruction_list)

        self.assertEqual(1, len(mail.outbox))

        sent_mail = mail.outbox[0]

        self.assertEqual("test@example.com", sent_mail.to[0])
        self.assertEqual("This is a test text", sent_mail.body)
        self.assertEqual("This is a test subject", sent_mail.subject)

    def test_send_email_with_variables(self):
        recipient = UserFactory.create(first_name="John", last_name="Doe")
        config = EmailConfig.objects.create()
        config.municipality = "Gemeente X"
        config.save()

        destruction_list = DestructionListFactory.create(name="Interesting List")
        email = AutomaticEmailFactory(
            body="This is a test email for {{ user }} "
            "from municipality {{ municipality }} about "
            "the list {{ list }} ({{ link_list }})",
            subject="This is a test subject",
        )

        email.send(recipient=recipient, destruction_list=destruction_list)

        self.assertEqual(1, len(mail.outbox))

        sent_mail = mail.outbox[0]

        list_url = get_absolute_url(
            reverse("destruction:dl-redirect", args=[destruction_list.pk])
        )
        expected_body = (
            f"This is a test email for John Doe from municipality Gemeente X about the "
            f"list Interesting List ({list_url})"
        )
        self.assertEqual(expected_body, sent_mail.body)
        self.assertEqual("This is a test subject", sent_mail.subject)

    def test_send_email_with_link_to_report(self):
        report = DestructionReportFactory.create()
        email = AutomaticEmailFactory(
            type=EmailTypeChoices.report_available,
            body="This is a link to the report: {{ link_report }}",
            subject="This is a test subject",
        )

        email.send(
            recipient=self.user, destruction_list=report.destruction_list, report=report
        )

        self.assertEqual(1, len(mail.outbox))

        sent_mail = mail.outbox[0]

        pdf_report_url = furl(
            get_absolute_url(reverse("report:download-report", args=[report.pk]))
        )
        pdf_report_url.args["type"] = ReportTypeChoices.pdf
        expected_body = f"This is a link to the report: {pdf_report_url.url}"

        self.assertEqual(expected_body, sent_mail.body)
