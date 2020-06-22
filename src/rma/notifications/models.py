from django.db import models
from django.utils.translation import ugettext_lazy as _


class Notification(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("user"),
    )
    destruction_list = models.ForeignKey(
        "destruction.DestructionList",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("destruction list"),
    )
    message = models.TextField(_("message"), max_length=1000)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

    def __str__(self):
        return f"{self.user} - {self.destruction_list}"
