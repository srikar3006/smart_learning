from django.urls import path

from . import views

app_name = "quizzes"

urlpatterns = [
    path("<slug:slug>/start/", views.quiz_start, name="start"),
    path("<slug:slug>/question/<int:order>/", views.quiz_question, name="question"),
    path("<slug:slug>/answer/", views.api_submit_answer, name="api_submit_answer"),
    path("<slug:slug>/result/", views.quiz_result, name="result"),
]
