from django import template
from django.db.models import Q
from django.urls import reverse

from archiefbeheercomponent.constants import RoleTypeChoices
from archiefbeheercomponent.report.utils import get_absolute_url

from ..models import DestructionList

register = template.Library()


@register.inclusion_tag("destruction/download_report.html", takes_context=True)
def download_report_link(context: dict, destruction_list: DestructionList) -> dict:
    request = context["view"].request

    report = destruction_list.destructionreport_set.first()

    tag_context = {"can_download": False}

    if not report:
        return tag_context

    if (
        report.process_owner != request.user
        and request.user.role.type != RoleTypeChoices.functional_admin
    ):
        return tag_context

    url = get_absolute_url(
        reverse("report:download-report", args=[report.pk]),
        request=context["view"].request,
    )
    tag_context.update(
        {
            "can_download": True,
            "url_csv": f"{url}?type=csv",
            "url_pdf": f"{url}?type=pdf",
        }
    )

    reviews = destruction_list.reviews.filter(~Q(additional_document__exact=""))
    if reviews.count():
        reviewers_documents_url = get_absolute_url(
            reverse(
                "destruction:download-reviewer-documents", args=[destruction_list.pk]
            ),
            request=context["view"].request,
        )

        tag_context["additional_documents"] = reviewers_documents_url

    return tag_context
