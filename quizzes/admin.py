from django.contrib import admin

from .models import Choice, Question, Quiz, QuizAnswer, QuizAttempt


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ("order", "text", "emoji", "image", "is_correct")


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True
    fields = ("order", "text", "image_prompt", "audio_prompt")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "rhyme", "question_count", "passing_score_pct")
    search_fields = ("title", "rhyme__title")
    list_filter = ("passing_score_pct",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "order", "text", "choice_count")
    list_filter = ("quiz",)
    search_fields = ("text", "quiz__title")
    inlines = [ChoiceInline]

    @admin.display(description="Choices")
    def choice_count(self, obj):
        return obj.choices.count()


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "total_questions", "stars", "completed_at")
    list_filter = ("quiz", "stars")
    search_fields = ("user__username", "quiz__title")
    readonly_fields = ("started_at", "completed_at")


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "choice", "is_correct", "answered_at")
    list_filter = ("is_correct",)
    search_fields = ("attempt__user__username", "question__text")
    readonly_fields = ("answered_at",)
