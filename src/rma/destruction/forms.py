import itertools
from typing import List, Tuple

from django import forms
from django.forms.models import BaseInlineFormSet

from rma.accounts.models import User

from .constants import Suggestion
from .models import (
    DestructionList,
    DestructionListAssignee,
    DestructionListItem,
    DestructionListReview,
)
from .service import get_zaaktypen


def get_zaaktype_choices() -> List[Tuple[str, list]]:
    zaaktypen = get_zaaktypen()
    zaaktypen = sorted(zaaktypen, key=lambda x: (x["omschrijving"], x["versiedatum"]))
    choices = []
    for key, group in itertools.groupby(zaaktypen, lambda x: x["omschrijving"]):
        group_choices = [
            (z["url"], f"Version {z['versiedatum']} - {z['identificatie']}")
            for z in group
        ]
        choices.append((key, group_choices))

    return choices


def get_reviewer_choices(author=None) -> List[Tuple[str, str]]:
    reviewers = User.objects.reviewers().order_by(
        "role__order", "last_name", "first_name", "username",
    )
    if author:
        reviewers.exclude(id=author.id)

    choices = []
    for user in reviewers:
        choices.append((user.id, user.as_reviewer_display()))

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
            destruction_list.assign(destruction_list.next_assignee())
            destruction_list.save()

    def save(self, **kwargs):
        destruction_list = super().save(**kwargs)

        self.save_items(destruction_list)
        self.save_assignees(destruction_list)

        return destruction_list


class ReviewForm(forms.ModelForm):
    class Meta:
        model = DestructionListReview
        fields = ("text", "status")


class ReviewItemBaseFormset(BaseInlineFormSet):
    def save(self, commit=True):
        # save only items with suggestions
        instances = super().save(commit=False)

        for instance in instances:
            if instance.suggestion:
                instance.save()


class ListItemForm(forms.ModelForm):
    action = forms.ChoiceField(required=False, choices=Suggestion.choices)
    archiefnominatie = forms.CharField(required=False)
    # used charfield for easy conversion into json
    archiefactiedatum = forms.CharField(required=False)

    class Meta:
        fields = ("action", "archiefnominatie", "archiefactiedatum")

    def save(self, commit=True):
        list_item = super().save(commit)
        action = self.cleaned_data.get("action")

        if action:
            list_item.remove()
            list_item.save()

        return list_item
