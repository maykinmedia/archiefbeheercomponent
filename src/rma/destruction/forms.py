from typing import List, Tuple

from django import forms

from rma.accounts.models import User

from .models import DestructionList, DestructionListAssignee, DestructionListItem
from .service import get_zaaktypen
from .tasks import process_destruction_list


def get_zaaktype_choices() -> List[Tuple[str, str]]:
    zaaktypen = get_zaaktypen()
    zaaktypen = sorted(zaaktypen, key=lambda x: (x["omschrijving"], x["versiedatum"]))
    choices = []
    for zaaktype in zaaktypen:
        label = f"{zaaktype['omschrijving']} ({zaaktype['versiedatum']})"
        choices.append((zaaktype["url"], label))

    return choices


def get_reviewer_choices(author=None) -> List[Tuple[str, str]]:
    reviewers = User.objects.reviewers().order_by("role__name", "username")
    if author:
        reviewers.exclude(id=author.id)

    choices = []
    for reviewer in reviewers:
        label = f"{reviewer.role.name} - {reviewer.get_full_name()}"
        choices.append((reviewer.id, label))

    choices.insert(0, ("", "-----"))
    return choices


class DestructionListForm(forms.ModelForm):
    zaken = forms.CharField()
    reviewer_1 = forms.ModelChoiceField(queryset=User.objects.reviewers().all())
    reviewer_2 = forms.ModelChoiceField(
        queryset=User.objects.reviewers().all(), required=False
    )

    class Meta:
        model = DestructionList
        fields = ("name", "zaken", "reviewer_1", "reviewer_2")

    def clean_zaken(self) -> List[str]:
        return self.cleaned_data["zaken"].split(",")

    def save_items(self, destruction_list):
        zaken = self.cleaned_data["zaken"]
        destruction_list_items = []
        for zaak in zaken:
            destruction_list_items.append(
                DestructionListItem(destruction_list=destruction_list, zaak=zaak)
            )
        DestructionListItem.objects.bulk_create(destruction_list_items)

    def save_assignees(self, destruction_list):
        assignees = []
        for i in range(1, 3):
            reviewer = self.cleaned_data[f"reviewer_{i}"]
            if reviewer:
                assignees.append(
                    DestructionListAssignee(
                        destruction_list=destruction_list, order=i, assignee=reviewer,
                    )
                )
        destruction_list_assignees = DestructionListAssignee.objects.bulk_create(
            assignees
        )
        if destruction_list_assignees:
            destruction_list.assignee = destruction_list_assignees[0].assignee
            destruction_list.save()

    def save(self, **kwargs):
        destruction_list = super().save(**kwargs)

        self.save_items(destruction_list)
        self.save_assignees(destruction_list)

        # TODO put it after reviews creation when reviews start existing
        process_destruction_list.delay(destruction_list.id)

        return destruction_list
