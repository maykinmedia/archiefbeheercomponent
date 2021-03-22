from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class ListStatus(DjangoChoices):
    in_progress = ChoiceItem("in_progress", "onderhanden")
    processing = ChoiceItem("processing", "wordt uitgevoerd")
    completed = ChoiceItem("completed", "uitgevoerd")


class ListItemStatus(DjangoChoices):
    suggested = ChoiceItem("suggested", _("suggested for destruction"))
    removed = ChoiceItem("removed", _("removed from the list during review"))
    processing = ChoiceItem("processing", _("is currently being destroyed"))
    destroyed = ChoiceItem("destroyed", _("successfully destroyed"))
    failed = ChoiceItem("failed", _("destruction did not succeed"))


class ReviewStatus(DjangoChoices):
    approved = ChoiceItem("approved", _("approved"))
    changes_requested = ChoiceItem("changes_requested", _("changes requested"))
    rejected = ChoiceItem("rejected", _("rejected"))


class Suggestion(DjangoChoices):
    remove = ChoiceItem("remove", _("remove"))
    change_and_remove = ChoiceItem("change_and_remove", _("change_and_remove"))


class ReviewerDisplay(DjangoChoices):
    reviewed = ChoiceItem("reviewed", "beoordeeld")
    to_review = ChoiceItem("to_review", "te beoordelen")
    all = ChoiceItem("all", "alle")


class ListStateDisplay(DjangoChoices):
    in_progress = ChoiceItem("in_progress", _("In progress"))
    changes_requested = ChoiceItem("changes_requested", _("Changes requested"))
    rejected = ChoiceItem("rejected", _("Rejected"))
    approved = ChoiceItem("approved", _("Approved"))
    finished = ChoiceItem("finished", _("Finished"))
