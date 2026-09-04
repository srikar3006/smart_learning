from django.contrib import admin

from .models import Choice, Question, Quiz, QuizAttempt


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ("text", "emoji", "image", "is_correct", "order")


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ("text", "audio_prompt", "image_prompt", "order")
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "rhyme", "passing_score_pct", "question_count")
    search_fields = ("title", "rhyme__title")
    autocomplete_fields = ("rhyme",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order")
    list_filter = ("quiz",)
    search_fields = ("text",)
    inlines = [ChoiceInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "total_questions", "stars", "completed_at")
    list_filter = ("quiz",)
    search_fields = ("user__username", "quiz__title")