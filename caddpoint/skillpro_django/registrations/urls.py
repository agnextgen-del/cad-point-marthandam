from django.urls import path

from . import dashboard_api, views

urlpatterns = [
    path("register", views.register, name="skillpro-register"),
    path("health", views.health, name="skillpro-health"),

    # JSON API for the dashboard page inside the website
    path("dash/session", dashboard_api.session),
    path("dash/login", dashboard_api.login_api),
    path("dash/logout", dashboard_api.logout_api),
    path("dash/list", dashboard_api.list_api),
    path("dash/delete/<int:pk>", dashboard_api.delete_api),
]
