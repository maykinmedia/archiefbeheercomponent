from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class EmailTypeChoices(DjangoChoices):
    report_available = ChoiceItem("report_available", _("Report available"))
    review_required = ChoiceItem("review_required", _("Review required"))
    changes_required = ChoiceItem("changes_required", _("Changes required"))
