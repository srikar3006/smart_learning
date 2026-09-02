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

    # Games
    path(
        "games/",
        include(("games.urls", "games"), namespace="games")
    ),

    # Standalone 50-level Quiz Challenge
    path(
        "quiz/",
        include(("quizzes.urls", "quizzes"), namespace="quiz_challenge")
    ),

    # Quizzes
    path(
        "quizzes/",
        include(("quizzes.urls", "quizzes"), namespace="quizzes")
    ),
]