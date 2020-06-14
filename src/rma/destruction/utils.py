from typing import List, Tuple

from .service import get_zaaktypen


def get_zaaktype_choices() -> List[Tuple[str, str]]:
    zaaktypen = get_zaaktypen()
    choices = []
    for zaaktype in zaaktypen:
        label = f"{zaaktype['omschrijving']} ({zaaktype['versiedatum']})"
        choices.append((zaaktype["url"], label))

    return choices
