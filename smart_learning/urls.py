from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # Main / Landing / Home
    path("", include("core.urls")),

    # Authentication
    path("accounts/", include("accounts.urls")),

    # Nursery Rhymes
    path(
        "rhymes/",
        include(("rhymes.urls", "rhymes"), namespace="rhymes")
    ),

    # Progress
    path(
        "progress/",
        include(("progress.urls", "progress"), namespace="progress")
    ),

    # Standalone 10-level Quiz Challenge
    path(
        "quiz/",
        include(("quizzes.challenge_urls", "quiz_challenge"), namespace="quiz_challenge")
    ),

    # Quizzes
    path(
        "quizzes/",
        include(("quizzes.urls", "quizzes"), namespace="quizzes")
    ),
]