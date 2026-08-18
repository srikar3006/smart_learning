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

    # Quizzes
    path(
        "quizzes/",
        include(("quizzes.urls", "quizzes"), namespace="quizzes")
    ),
]