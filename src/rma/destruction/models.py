from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_fsm import FSMField, transition

from .constants import ListItemStatus, ListStatus, ReviewStatus, Suggestion


class DestructionList(models.Model):
    name = models.CharField(_("name"), max_length=200, unique=True)
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="created_lists",
        verbose_name=_("author"),
        help_text=_("Creator of destruction list."),
    )
    created = models.DateTimeField(_("created"), auto_now=True)
    end = models.DateTimeField(_("end"), blank=True, null=True)
    assignee = models.ForeignKey(
        "accounts.User",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="assigned_lists",
        verbose_name=_("assignee"),
        help_text=_("Currently assigned user."),
    )
    status = FSMField(
        _("status"),
        default=ListStatus.in_progress,
        choices=ListStatus.choices,
        protected=True,
        max_length=80,
    )

    class Meta:
        verbose_name = _("destruction list")
        verbose_name_plural = _("destruction lists")

    def __str__(self):
        return self.name

    @transition(
        field=status, source=ListStatus.in_progress, target=ListStatus.processing
    )
    def process(self):
        pass

    @transition(field=status, source=ListStatus.processing, target=ListStatus.completed)
    def complete(self):
        self.end = timezone.now()


class DestructionListItem(models.Model):
    destruction_list = models.ForeignKey(
        DestructionList,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("destruction list"),
    )
    zaak = models.URLField(
        _("zaak"),
        help_text=_(
            "URL-reference to the ZAAK (in Zaken API), which is planned to be destroyed."
        ),
    )
    status = FSMField(
        _("status"),
        default=ListItemStatus.suggested,
        choices=ListItemStatus.choices,
        protected=True,
        max_length=80,
    )

    class Meta:
        verbose_name = _("destruction list item")
        verbose_name_plural = _("destruction list items")
        unique_together = ("destruction_list", "zaak")

    def __str__(self):
        return f"{self.destruction_list}: {self.zaak}"

    @transition(
        field=status, source=ListItemStatus.suggested, target=ListItemStatus.removed
    )
    def remove(self):
        pass

    @transition(
        field=status, source=ListItemStatus.suggested, target=ListItemStatus.processing
    )
    def process(self):
        pass

    @transition(
        field=status,
        source=ListItemStatus.processing,
        target=ListItemStatus.destroyed,
        on_error=ListItemStatus.failed,
    )
    def complete(self, request, by):
        # extra args to make fsm-admin work
        pass


class DestructionListReview(models.Model):
    destruction_list = models.ForeignKey(
        DestructionList,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("destruction list"),
    )
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("author"),
        help_text=_("User, who performed review"),
    )
    created = models.DateTimeField(_("created"), auto_now=True)
    text = models.TextField(
        _("text"),
        max_length=2000,
        blank=True,
        help_text=_("Review comments on the destruction list in general"),
    )
    status = models.CharField(
        _("status"), blank=True, choices=ReviewStatus.choices, max_length=80
    )

    class Meta:
        verbose_name = _("destruction list review")
        verbose_name_plural = _("destruction list reviews")

    def __str__(self):
        return f"{self.destruction_list}: {self.author}"


class DestructionListItemReview(models.Model):
    destruction_list_review = models.ForeignKey(
        DestructionListReview,
        on_delete=models.CASCADE,
        related_name="item_reviews",
        verbose_name=_("destruction list review"),
    )
    destruction_list_item = models.ForeignKey(
        DestructionListItem,
        on_delete=models.CASCADE,
        related_name="item_reviews",
        verbose_name=_("destruction list item"),
    )
    text = models.TextField(
        _("text"),
        max_length=2000,
        blank=True,
        help_text=_("Review comments on the destruction list item"),
    )
    suggestion = models.CharField(
        _("suggestion"), blank=True, choices=Suggestion.choices, max_length=80
    )

    class Meta:
        verbose_name = _("destruction list item review")
        verbose_name_plural = _("destruction list item reviews")

    def __str__(self):
        return f"({self.destruction_list_review}) - ({self.destruction_list_item})"
