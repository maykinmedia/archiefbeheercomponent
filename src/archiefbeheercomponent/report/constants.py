from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class ReportTypeChoices(DjangoChoices):
    pdf = ChoiceItem("pdf", _("PDF"))
    csv = ChoiceItem("csv", _("CSV"))
