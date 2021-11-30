import itertools
from typing import List, Tuple

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from archiefvernietigingscomponent.accounts.models import User

from .constants import Suggestion, ZaakArchiefnominatieChoices
from .models import (
    ArchiveConfig,
    DestructionList,
    DestructionListAssignee,
    DestructionListItem,
    DestructionListReview,
    DestructionListReviewComment,
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
    zaken_identificaties = SimpleArrayField(forms.CharField(max_length=250))

    class Meta:
        model = DestructionList
        fields = (
            "name",
            "zaken",
            "reviewer_1",
            "reviewer_2",
            "zaken_identificaties",
            "contains_sensitive_info",
        )

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


class ReviewCommentForm(forms.ModelForm):
    class Meta:
        model = DestructionListReviewComment
        fields = ("text",)


class ReviewItemBaseForm(forms.ModelForm):
    identificatie = forms.CharField()

    class Meta:
        fields = ["destruction_list_item", "text", "suggestion", "identificatie"]

    def save(self, commit=True):
        # save only items with suggestions
        instance = super().save(commit=False)

        if instance.suggestion:
            instance.save()


class ListItemForm(forms.ModelForm):
    action = forms.ChoiceField(required=False, choices=Suggestion.choices)
    archiefnominatie = forms.CharField(required=False)
    # used charfield for easy conversion into json
    archiefactiedatum = forms.CharField(required=False)
    identificatie = forms.CharField()

    class Meta:
        fields = ("action", "archiefnominatie", "archiefactiedatum", "identificatie")

    def save(self, commit=True):
        list_item = super().save(commit)
        action = self.cleaned_data.get("action")

        if action:
            list_item.remove()
            list_item.save()

        return list_item


class ArchiveConfigForm(forms.ModelForm):
    class Meta:
        model = ArchiveConfig
        fields = (
            "archive_date",
            "link_to_zac",
            "short_review_zaaktypes",
            "days_until_reminder",
            "create_zaak",
            "source_organisation",
            "case_type",
            "status_type",
            "result_type",
            "document_type",
        )

    def clean(self):
        super().clean()
        if self.cleaned_data["create_zaak"]:
            error = ValidationError(
                _(
                    "If '%(create_zaak_label)s' is checked, "
                    "all the other destruction case settings need to be configured."
                )
                % {"create_zaak_label": self.fields["create_zaak"].label},
                code="invalid",
            )

            required_fields = [
                "source_organisation",
                "case_type",
                "status_type",
                "result_type",
                "document_type",
            ]
            for required_field in required_fields:
                if not self.cleaned_data.get(required_field):
                    self.add_error("create_zaak", error)
                    return

    def save(self, commit=True):
        instance = super().save(commit)

        # Case in which all the checkboxes have been unticked. It gets interpreted as if the field hasn't changed.
        # So we set an empty list of zaaktypes manually
        if (
            "short_review_zaaktypes" not in self.changed_data
            and "short_review_zaaktypes" in self.cleaned_data
        ):
            if self.cleaned_data["short_review_zaaktypes"] is None:
                instance.short_review_zaaktypes = []
                instance.save()

        return instance


class ZaakArchiveDetailsForm(forms.Form):
    url = forms.URLField(required=True)
    archiefnominatie = forms.ChoiceField(
        choices=ZaakArchiefnominatieChoices.choices,
        widget=forms.RadioSelect,
        required=False,
    )
    archiefactiedatum = forms.DateField(widget=forms.SelectDateWidget, required=False)
    comment = forms.CharField(
        widget=forms.Textarea(attrs={"cols": "50", "rows": "5"}), required=False
    )

    class Meta:
        fields = ("url", "archiefnominatie", "archiefactiedatum", "comment")
