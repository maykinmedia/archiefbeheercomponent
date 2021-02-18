from django import template

from ..models import ThemeConfig

register = template.Library()


@register.inclusion_tag("theme/stylesheet.html")
def theme_stylesheet() -> dict:
    return {"config": ThemeConfig.get_solo()}


@register.inclusion_tag("theme/footer_content.html")
def theme_footer() -> dict:
    return {"config": ThemeConfig.get_solo()}


@register.inclusion_tag("theme/header_content.html")
def theme_header() -> dict:
    return {"config": ThemeConfig.get_solo()}
