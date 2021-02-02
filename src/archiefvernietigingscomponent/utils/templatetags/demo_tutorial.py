from django import template

from archiefvernietigingscomponent.accounts.models import User

register = template.Library()


@register.inclusion_tag("demo/demo_tutorial.html")
def demo_tutorial(current_user: User) -> dict:
    demo_users = User.objects.filter(username__startswith="demo")
    return {"demo_users": demo_users, "current_user": current_user}
