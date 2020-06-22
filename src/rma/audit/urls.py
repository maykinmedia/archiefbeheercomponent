from django.urls import path

from .views import AuditTrailView

app_name = "audit"

urlpatterns = [
    path("", AuditTrailView.as_view(), name="audit-trail"),
]
