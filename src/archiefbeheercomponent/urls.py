from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from mozilla_django_oidc_db.views import AdminLoginFailure

from archiefbeheercomponent.accounts.views import StartPageView
from archiefbeheercomponent.demo.views import DemoLoginView
from archiefbeheercomponent.destruction.views.redirect import EnterView

handler500 = "archiefbeheercomponent.utils.views.server_error"
admin.site.site_header = "archiefbeheercomponent admin"
admin.site.site_title = "archiefbeheercomponent admin"
admin.site.index_title = "Welcome to the archiefbeheercomponent admin"

urlpatterns = [
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path("admin/login/failure/", AdminLoginFailure.as_view(), name="admin-oidc-error"),
    path("admin/hijack/", include("hijack.urls")),
    path("admin/", admin.site.urls),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # auth backends
    path("adfs/", include("django_auth_adfs.urls")),
    path("oidc/", include("mozilla_django_oidc.urls")),
    # Simply show the master template.
    path("", EnterView.as_view(), name="entry"),
    path("vernietigen/", include("archiefbeheercomponent.destruction.urls")),
    path("reports/", include("archiefbeheercomponent.report.urls")),
    path("emails/", include("archiefbeheercomponent.emails.urls")),
    path("audit/", include("archiefbeheercomponent.audit.urls")),
    path("demo/<int:pk>/", DemoLoginView.as_view(), name="demo-login"),
    path("startpage/", StartPageView.as_view(), name="start-page"),
]

# NOTE: The staticfiles_urlpatterns also discovers static files (ie. no need to run collectstatic). Both the static
# folder and the media folder are only served via Django if DEBUG = True.
urlpatterns += staticfiles_urlpatterns() + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG and apps.is_installed("debug_toolbar"):
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
