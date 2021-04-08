from django import forms
from django.db.models import F, Q

from django_filters import ChoiceFilter, FilterSet

from .constants import ListStatus, RecordManagerDisplay, ReviewerDisplay
from .models import DestructionList


class ReviewerListFilter(FilterSet):
    reviewed = ChoiceFilter(
        field_name="reviewed",
        label="lists for reviewer",
        choices=ReviewerDisplay.choices,
        method="filter_reviewed",
        empty_label=None,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = DestructionList
        fields = ("reviewed",)

    def __init__(self, data, *args, **kwargs):
        data = data or {}
        if not data.get("reviewed"):
            data["reviewed"] = ReviewerDisplay.to_review

        super().__init__(data, *args, **kwargs)

    def filter_reviewed(self, queryset, name, value):
        user = self.request.user
        if value == ReviewerDisplay.to_review:
            return queryset.filter(assignee=user)
        elif value == ReviewerDisplay.reviewed:
            return queryset.filter(~Q(assignee=user))
        else:
            return queryset


class RecordManagerListFilter(FilterSet):
    list_status = ChoiceFilter(
        field_name="list_status",
        label="lists for record manager",
        choices=RecordManagerDisplay.choices,
        method="filter_list_status",
        empty_label=None,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = DestructionList
        fields = ("list_status",)

    def __init__(self, data, *args, **kwargs):
        data = data or {}
        if not data.get("list_status"):
            data["list_status"] = RecordManagerDisplay.all

        super().__init__(data, *args, **kwargs)

    def filter_list_status(self, queryset, name, value):
        if value == RecordManagerDisplay.in_progress:
            return queryset.filter(
                Q(status=ListStatus.in_progress) | Q(status=ListStatus.processing),
                ~Q(author=F("assignee")) | Q(assignee__isnull=True),
            )
        elif value == RecordManagerDisplay.completed:
            return queryset.filter(status=ListStatus.completed)
        elif value == RecordManagerDisplay.action_required:
            return queryset.filter(
                Q(status=ListStatus.in_progress), Q(author=F("assignee"))
            )
        else:
            return queryset
