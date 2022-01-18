from django.urls import path

from archiefbeheercomponent.emails.views import EmailPreferenceUpdateView

app_name = "emails"

urlpatterns = [
    path(
        "email_preference/<int:pk>/",
        EmailPreferenceUpdateView.as_view(),
        name="email-preference-update",
    )
]
