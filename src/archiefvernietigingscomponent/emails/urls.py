from django.urls import path

from archiefvernietigingscomponent.emails.views import EmailPreferenceUpdateView

app_name = "emails"

urlpatterns = [
    path(
        "email_preference/<int:pk>/",
        EmailPreferenceUpdateView.as_view(),
        name="email-preference-update",
    )
]
