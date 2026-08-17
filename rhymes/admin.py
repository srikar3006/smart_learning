from django.contrib import admin

from .models import Category, Rhyme


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_emoji", "order", "rhyme_count")
    search_fields = ("name",)
    ordering = ("order", "name")

    @admin.display(description="Lessons")
    def rhyme_count(self, obj):
        return obj.rhymes.count()


@admin.register(Rhyme)
class RhymeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "difficulty",
        "media_state",
        "quiz_state",
        "is_published",
        "order",
    )
    list_filter = ("category", "difficulty", "is_published")
    search_fields = ("title", "lyrics", "description")
    prepopulated_fields = {"slug": ("title",)}
    list_select_related = ("category",)

    @admin.display(description="Media")
    def media_state(self, obj):
        return "Ready" if obj.media_available else "Fallback voice"

    @admin.display(description="Quiz")
    def quiz_state(self, obj):
        return "Configured" if obj.has_quiz and obj.quiz.question_count else "Not ready"
