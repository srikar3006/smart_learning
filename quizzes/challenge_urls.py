from django.urls import path

from . import views

app_name = "quiz_challenge"

urlpatterns = [
    path("", views.quiz_dashboard, name="dashboard"),
    path("level/<int:level>/", views.quiz_level, name="level"),
    path("level/<int:level>/result/", views.quiz_level_result, name="level_result"),
    path("level/<int:level>/submit/", views.api_submit_level, name="submit_level"),
]
