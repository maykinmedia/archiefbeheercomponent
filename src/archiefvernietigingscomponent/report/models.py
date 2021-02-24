import uuid as _uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from privates.fields import PrivateMediaFileField

from archiefvernietigingscomponent.constants import RoleTypeChoices


class DestructionReport(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name=_("title"),
        help_text=_("Title of the destruction report"),
    )
    process_owner = models.ForeignKey(
        to="accounts.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("process owner"),
        help_text=_(
            "Process owner of the destruction list for which the report was created"
        ),
    )
    content = PrivateMediaFileField(
        verbose_name=_("content"),
        upload_to="reports/%Y/%m/",
        help_text=_("Content of the destruction report"),
    )
    destruction_list = models.ForeignKey(
        to="destruction.DestructionList",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("destruction list"),
        help_text=_("Destruction list for which the report was created."),
    )

    class Meta:
        verbose_name = _("Destruction report")
        verbose_name_plural = _("Destruction reports")

    def __str__(self):
        return self.title

    def clean(self):
        if (
            self.process_owner
            and self.process_owner.role.type != RoleTypeChoices.process_owner
        ):
            error_message = _(
                "Only a process owner can be associated with a destruction report"
            )
            raise ValidationError(error_message)
