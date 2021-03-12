from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import ugettext_lazy as _

from archiefvernietigingscomponent.accounts.models import User
from archiefvernietigingscomponent.emails.constants import (
    EmailPreferenceChoices,
    EmailTypeChoices,
)
from archiefvernietigingscomponent.report.models import DestructionReport


class AutomaticEmail(models.Model):
    type = models.CharField(
        _("type"),
        max_length=200,
        help_text=_("The type of email"),
        choices=EmailTypeChoices,
        unique=True,
    )
    body = models.TextField(_("body"), help_text=_("The text sent in the email body"))
    subject = models.CharField(
        _("subject"), max_length=200, help_text=_("The text sent in the email subject")
    )

    class Meta:
        verbose_name = _("Automatic email")
        verbose_name_plural = _("Automatic emails")

    def __str__(self):
        return f"Automatic email ({self.type})"

    def send(self, recipient: User, report: DestructionReport = None):
        email = EmailMessage(
            subject=self.subject,
            body=self.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email],
        )
        if report:
            email.attach(
                filename=report.get_filename(),
                content=report.content_pdf.read(),
                mimetype="application/pdf",
            )
        email.send()


class EmailPreference(models.Model):
    user = models.OneToOneField(
        to=User,
        verbose_name=_("user"),
        help_text=_("User associated with the preferences"),
        on_delete=models.CASCADE,
    )
    preference = models.CharField(
        max_length=100,
        choices=EmailPreferenceChoices,
        default=EmailPreferenceChoices.action_required,
    )

    class Meta:
        verbose_name = _("Email preference")
        verbose_name_plural = _("Email preferences")

    def __str__(self):
        return f"Email preferences of user {self.user}"
