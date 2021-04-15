from django import forms
from django.db.models import Q

from django_filters import ChoiceFilter, FilterSet

from .constants import ReviewerDisplay
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
