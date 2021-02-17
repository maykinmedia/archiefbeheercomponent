from django.views.generic import TemplateView


class StartPageView(TemplateView):
    template_name = "start_page/content_start_page.html"
