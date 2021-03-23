import copy
import logging
import re

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from solo.models import SingletonModel

from archiefvernietigingscomponent.accounts.models import User
from archiefvernietigingscomponent.emails.constants import (
    EmailPreferenceChoices,
    EmailTypeChoices,
)

logger = logging.getLogger(__name__)


USER_TEMPLATE_ELEMENT = "{{ user }}"
MUNICIPALITY_TEMPLATE_ELEMENT = "{{ municipality }}"
DL_TEMPLATE_ELEMENT = "{{ list }}"
LINK_DL_TEMPLATE_ELEMENT = "{{ link_list }}"
LINK_REPORT_TEMPLATE_ELEMENT = "{{ link_report }}"

EMAIL_TEMPLATE_ELEMENTS = (
    USER_TEMPLATE_ELEMENT,
    MUNICIPALITY_TEMPLATE_ELEMENT,
    DL_TEMPLATE_ELEMENT,
    LINK_DL_TEMPLATE_ELEMENT,
    LINK_REPORT_TEMPLATE_ELEMENT,
)


class EmailConfig(SingletonModel):
    municipality = models.CharField(
        _("municipality"),
        max_length=200,
        help_text=_("The municipality on behalf of which the emails are sent."),
    )

    class Meta:
        verbose_name = _("email configuration")


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

    def send(
        self, recipient, destruction_list, report=None,
    ):
        """
        :param recipient: type User
        :param destruction_list: type DestructionList:
        :param report: type DestructionReport (optional)
        :rtype: None
        """
        email = EmailMessage(
            subject=self.subject,
            body=self.compose_body(recipient, destruction_list, report),
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

    def compose_body(self, recipient, destruction_list, report=None) -> str:
        """
        :param recipient: type User
        :param destruction_list: type DestructionList:
        :param report: type DestructionReport (optional)
        :rtype: str
        """
        from archiefvernietigingscomponent.report.utils import get_absolute_url

        filled_body = copy.copy(self.body)

        for pattern in EMAIL_TEMPLATE_ELEMENTS:
            if re.search(pattern, filled_body):
                re_pattern = re.compile(pattern)

                if pattern == USER_TEMPLATE_ELEMENT:
                    value = recipient.get_full_name()
                elif pattern == MUNICIPALITY_TEMPLATE_ELEMENT:
                    email_config = EmailConfig.get_solo()
                    value = email_config.municipality
                    if value == "":
                        logger.warning("Municipality name is an empty string!")
                elif pattern == DL_TEMPLATE_ELEMENT:
                    value = destruction_list.name
                elif pattern == LINK_DL_TEMPLATE_ELEMENT:
                    value = get_absolute_url(
                        reverse("destruction:dl-redirect", args=[destruction_list.pk])
                    )
                elif pattern == LINK_REPORT_TEMPLATE_ELEMENT:
                    value = get_absolute_url(
                        reverse("report:download-report", args=[report.pk]),
                    )

                filled_body = re.sub(re_pattern, value, filled_body)

        return filled_body


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
