from django.urls import path

from . import views

app_name = "quizzes"

urlpatterns = [
    # Quiz list
    path("", views.quiz_list, name="list"),

    # Start a quiz
    path(
        "<slug:slug>/start/",
        views.quiz_start,
        name="start",
    ),

    # Quiz question
    path(
        "<slug:slug>/question/<int:order>/",
        views.quiz_question,
        name="question",
    ),

    # Submit answer
    path(
        "<slug:slug>/answer/",
        views.api_submit_answer,
        name="api_submit_answer",
    ),

    # Quiz result
    path(
        "<slug:slug>/result/",
        views.quiz_result,
        name="result",
    ),
]