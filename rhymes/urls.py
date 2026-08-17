from django.urls import path

from . import views

app_name = "rhymes"

urlpatterns = [
    path("", views.rhyme_list, name="list"),
    path("<slug:slug>/", views.rhyme_detail, name="detail"),
    path("<slug:slug>/log-play/", views.api_log_play, name="api_log_play"),
    path("<slug:slug>/log-repeat/", views.api_log_repeat, name="api_log_repeat"),
    path("<slug:slug>/mark-complete/", views.api_mark_complete, name="api_mark_complete"),
]
