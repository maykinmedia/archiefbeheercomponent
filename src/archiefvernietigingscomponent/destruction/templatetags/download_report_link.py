from django import template
from django.urls import reverse

from archiefvernietigingscomponent.constants import RoleTypeChoices
from archiefvernietigingscomponent.destruction.models import DestructionList
from archiefvernietigingscomponent.report.utils import get_absolute_url

register = template.Library()


@register.inclusion_tag("destruction/download_report.html", takes_context=True)
def download_report_link(context: dict, destruction_list: DestructionList) -> dict:
    request = context["view"].request

    report = destruction_list.destructionreport_set.first()

    if not report:
        return {"can_download": False}

    if (
        report.process_owner == request.user
        or request.user.role.type == RoleTypeChoices.functional_admin
    ):
        url = get_absolute_url(
            reverse("report:download-report", args=[report.pk]),
            request=context["view"].request,
        )
        return {
            "can_download": True,
            "url_csv": f"{url}?type=csv",
            "url_pdf": f"{url}?type=pdf",
        }

    return {"can_download": False}
