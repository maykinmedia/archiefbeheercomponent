from django import forms
from django.contrib import admin
from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from solo.admin import SingletonModelAdmin

from .models import ThemeConfig


class ThemeConfigAdminForm(forms.ModelForm):
    class Meta:
        model = ThemeConfig
        widgets = {
            "address": widgets.Textarea(),
        }
        fields = "__all__"


@admin.register(ThemeConfig)
class ThemeConfigAdmin(SingletonModelAdmin):
    form = ThemeConfigAdminForm
    fieldsets = (
        (None, {"fields": ("logo",)}),
        (
            _("Text"),
            {"fields": ("organization_name", "tagline", "phone_number", "address",)},
        ),
        (
            _("Colors"),
            {
                "fields": (
                    "color_primary",
                    "color_primary_light",
                    "color_secondary",
                    "color_link",
                    "color_link_dark",
                ),
            },
        ),
    )
