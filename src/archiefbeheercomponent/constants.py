from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class RoleTypeChoices(DjangoChoices):
    archivist = ChoiceItem("archivist", _("Archivist"))
    record_manager = ChoiceItem("record_manager", _("Record manager"))
    process_owner = ChoiceItem("process_owner", _("Process owner"))
    functional_admin = ChoiceItem("functional_admin", _("Functional administrator"))
    other = ChoiceItem("other", _("Other"))
