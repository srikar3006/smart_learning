from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Smart Learning Administration"
admin.site.site_title = "Smart Learning Admin"
admin.site.index_title = "Platform management"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("rhymes/", include("rhymes.urls")),
    path("quiz/", include("quizzes.urls")),
    path("progress/", include("progress.urls")),
    path("parent/", include(("core.parent_urls", "parent"), namespace="parent")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
