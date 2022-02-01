from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class ListStatus(DjangoChoices):
    in_progress = ChoiceItem("in_progress", "onderhanden")
    processing = ChoiceItem("processing", "wordt uitgevoerd")
    completed = ChoiceItem("completed", "uitgevoerd")


class ListItemStatus(DjangoChoices):
    suggested = ChoiceItem("suggested", _("suggested for destruction"))
    removed = ChoiceItem(
        "removed", _("removed from the destruction list during review")
    )
    processing = ChoiceItem("processing", _("is currently being destroyed"))
    destroyed = ChoiceItem("destroyed", _("successfully destroyed"))
    failed = ChoiceItem("failed", _("destruction did not succeed"))


class ReviewStatus(DjangoChoices):
    approved = ChoiceItem("approved", _("approved"))
    changes_requested = ChoiceItem("changes_requested", _("changes requested"))
    rejected = ChoiceItem("rejected", _("rejected"))


class Suggestion(DjangoChoices):
    remove = ChoiceItem("remove", _("remove"))
    change_and_remove = ChoiceItem("change_and_remove", _("change and remove"))


class ReviewerDisplay(DjangoChoices):
    reviewed = ChoiceItem("reviewed", "beoordeeld")
    to_review = ChoiceItem("to_review", "te beoordelen")
    all = ChoiceItem("all", "alle")


class RecordManagerDisplay(DjangoChoices):
    in_progress = ChoiceItem("in_progress", _("In progress"))
    action_required = ChoiceItem("action_required", _("Action required"))
    completed = ChoiceItem("completed", _("Completed"))
    all = ChoiceItem("all", _("All"))


class ListStateDisplay(DjangoChoices):
    in_progress = ChoiceItem("in_progress", _("In progress"))
    changes_requested = ChoiceItem("changes_requested", _("Changes requested"))
    rejected = ChoiceItem("rejected", _("Rejected"))
    approved = ChoiceItem("approved", _("Approved"))
    finished = ChoiceItem("finished", _("Finished"))


# Taken from VNG API common
class Archiefnominatie(DjangoChoices):
    blijvend_bewaren = ChoiceItem(
        "blijvend_bewaren",
        _(
            "Het zaakdossier moet bewaard blijven en op de Archiefactiedatum overgedragen worden naar een "
            "archiefbewaarplaats."
        ),
    )
    vernietigen = ChoiceItem(
        "vernietigen",
        _("Het zaakdossier moet op of na de Archiefactiedatum vernietigd worden."),
    )


class Archiefstatus(DjangoChoices):
    nog_te_archiveren = ChoiceItem(
        "nog_te_archiveren",
        _("De zaak cq. het zaakdossier is nog niet als geheel gearchiveerd."),
    )
    gearchiveerd = ChoiceItem(
        "gearchiveerd",
        _(
            "De zaak cq. het zaakdossier is als geheel niet-wijzigbaar bewaarbaar gemaakt."
        ),
    )
    gearchiveerd_procestermijn_onbekend = ChoiceItem(
        "gearchiveerd_procestermijn_onbekend",
        _(
            "De zaak cq. het zaakdossier is als geheel niet-wijzigbaar bewaarbaar gemaakt maar de vernietigingsdatum "
            "kan nog niet bepaald worden."
        ),
    )
    overgedragen = ChoiceItem(
        "overgedragen",
        _("De zaak cq. het zaakdossier is overgebracht naar een archiefbewaarplaats."),
    )
