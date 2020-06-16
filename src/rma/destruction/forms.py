from typing import List, Tuple

from django import forms

from .models import DestructionList, DestructionListItem
from .service import get_zaaktypen


def get_zaaktype_choices() -> List[Tuple[str, str]]:
    zaaktypen = get_zaaktypen()
    zaaktypen = sorted(zaaktypen, key=lambda x: (x["omschrijving"], x["versiedatum"]))
    choices = []
    for zaaktype in zaaktypen:
        label = f"{zaaktype['omschrijving']} ({zaaktype['versiedatum']})"
        choices.append((zaaktype["url"], label))

    return choices


class DestructionListForm(forms.ModelForm):
    zaken = forms.CharField()

    class Meta:
        model = DestructionList
        fields = ("name", "assignee", "zaken")

    def clean_zaken(self):
        return self.cleaned_data["zaken"].split(",")

    def save(self, **kwargs):
        destruction_list = super().save(**kwargs)

        #  create items with zaak urls
        zaken = self.cleaned_data["zaken"]
        destruction_list_items = []
        for zaak in zaken:
            destruction_list_items.append(
                DestructionListItem(destruction_list=destruction_list, zaak=zaak)
            )
        DestructionListItem.objects.bulk_create(destruction_list_items)

        return destruction_list
