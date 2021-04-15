import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from archiefvernietigingscomponent.emails.constants import (
    EmailPreferenceChoices,
    EmailTypeChoices,
)
from archiefvernietigingscomponent.emails.models import (
    EMAIL_TEMPLATE_ELEMENTS,
    LINK_REPORT_TEMPLATE_ELEMENT,
    MUNICIPALITY_TEMPLATE_ELEMENT,
    AutomaticEmail,
    EmailConfig,
    EmailPreference,
)


class AutomaticEmailForm(forms.ModelForm):
    class Meta:
        model = AutomaticEmail
        fields = ("type", "subject", "body")

    def clean(self):
        # Check the template elements
        matches = set(re.findall(r"{{ .+? }}", self.data["body"]))

        for match in matches:
            if match not in EMAIL_TEMPLATE_ELEMENTS:
                raise ValidationError(_("Unknown variable used in the email body."))

            if (
                self.data["type"] != EmailTypeChoices.report_available
                and match == LINK_REPORT_TEMPLATE_ELEMENT
            ):
                raise ValidationError(
                    _(
                        "Cannot include the report link in the body of this type of email."
                    )
                )

            if match == MUNICIPALITY_TEMPLATE_ELEMENT:
                config = EmailConfig.get_solo()
                if not config.municipality:
                    raise ValidationError(
                        _(
                            "When using the municipality variable, a municipality name needs to be configured."
                        )
                    )


class EmailPreferenceAdminForm(forms.ModelForm):
    preference = forms.ChoiceField(
        label=_("Notify via email:"), choices=EmailPreferenceChoices.choices
    )

    class Meta:
        model = EmailPreference
        fields = ("preference",)
