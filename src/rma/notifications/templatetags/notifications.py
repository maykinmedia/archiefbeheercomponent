from typing import Any, Dict

from django.template import Library

from rma.accounts.models import User

from ..models import Notification

register = Library()


@register.inclusion_tag("notifications/includes/notifications.html")
def render_notifications(user: User, amount=10) -> Dict[str, Any]:
    """
    Render the notifications for the passed in user.
    """
    qs = (
        Notification.objects.filter(user=user)
        .select_related("destruction_list")
        .order_by("-created")
    )[:amount]
    return {"notifications": qs}
