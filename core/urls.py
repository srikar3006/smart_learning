from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("videos/", views.videos, name="videos"),
    path("games/", views.games, name="games"),
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings_page, name="settings"),
]
