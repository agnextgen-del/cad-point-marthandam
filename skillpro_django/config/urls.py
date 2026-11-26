from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

from registrations import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/skillpro/", include("registrations.urls")),

    # ---- Dashboard (staff login required) ----
    path("skillpro/registrations/", dashboard.dashboard, name="skillpro-dashboard"),
    path("skillpro/registrations/export.csv", dashboard.export_csv, name="skillpro-export"),
    path("skillpro/registrations/export.xlsx", dashboard.export_excel, name="skillpro-export-xlsx"),
    path("skillpro/registrations/<int:pk>/delete/", dashboard.delete_registration, name="skillpro-delete"),
    path("accounts/login/", LoginView.as_view(), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
]

# Serve the website itself from Django (local testing). On a live server use Nginx/Apache instead.
if settings.SERVE_SITE:
    urlpatterns += [
        path("", RedirectView.as_view(url="/" + settings.HOME_PAGE)),
        re_path(r"^(?P<path>.*)$", serve, {"document_root": settings.SITE_DIR}),
    ]
