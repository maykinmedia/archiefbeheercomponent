from django import forms

from .constants import ReportTypeChoices


class ReportTypeForm(forms.Form):
    type = forms.ChoiceField(
        choices=ReportTypeChoices.choices, help_text="Type of report"
    )
