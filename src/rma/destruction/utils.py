from typing import List, Tuple

from .service import get_zaaktypen


def get_zaaktype_choices() -> List[Tuple[str, str]]:
    zaaktypen = get_zaaktypen()
    zaaktypen = sorted(zaaktypen, key=lambda x: (x["omschrijving"], x["versiedatum"]))
    choices = []
    for zaaktype in zaaktypen:
        label = f"{zaaktype['omschrijving']} ({zaaktype['versiedatum']})"
        choices.append((zaaktype["url"], label))

    return choices
