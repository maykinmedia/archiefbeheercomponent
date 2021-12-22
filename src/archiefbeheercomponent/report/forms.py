from django import forms


class ReportTypeForm(forms.Form):
    type = forms.ChoiceField(
        choices=[("csv", "csv"), ("pdf", "pdf"),], help_text="Type of report"
    )
