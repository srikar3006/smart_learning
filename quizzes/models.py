from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from rhymes.models import Rhyme


class Quiz(models.Model):
    """One gamified quiz attached to a single rhyme."""
    rhyme = models.OneToOneField(
        Rhyme,
        on_delete=models.CASCADE,
        related_name="quiz",
    )
    title = models.CharField(max_length=150)
    passing_score_pct = models.PositiveIntegerField(default=60)

    def clean(self):
        if not 0 <= self.passing_score_pct <= 100:
            raise ValidationError(
                {
                    "passing_score_pct": (
                        "Passing score must be between 0 and 100."
                    )
                }
            )

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    text = models.CharField(
        max_length=255,
        help_text="Keep it short and simple for early readers.",
    )
    audio_prompt = models.FileField(
        upload_to="quiz/audio_prompts/",
        blank=True,
        null=True,
        help_text="Optional spoken prompt.",
    )
    image_prompt = models.ImageField(
        upload_to="quiz/image_prompts/",
        blank=True,
        null=True,
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["quiz", "order"],
                name="unique_quiz_question_order",
            ),
        ]

    def __str__(self):
        return f"{self.quiz.title} – Q{self.order}: {self.text}"


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    text = models.CharField(max_length=150, blank=True)
    emoji = models.CharField(max_length=8, blank=True)
    image = models.ImageField(
        upload_to="quiz/choice_images/",
        blank=True,
        null=True,
    )
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["question", "order"],
                name="unique_question_choice_order",
            ),
        ]

    def clean(self):
        if not self.text and not self.emoji and not self.image:
            raise ValidationError(
                "A choice needs text, an emoji, or an image."
            )

    def display_label(self):
        return self.emoji or self.text or "Option"

    def __str__(self):
        return f"{self.question} → {self.display_label()}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    stars = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(
                fields=["user", "completed_at"]
            ),
            models.Index(
                fields=["quiz", "completed_at"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} – {self.quiz.title} "
            f"({self.score}/{self.total_questions})"
        )

    @property
    def score_pct(self):
        if not self.total_questions:
            return 0
        return round(
            self.score / self.total_questions * 100
        )


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="picked_by",
    )
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="unique_attempt_question_answer",
            ),
        ]

    def __str__(self):
        return (
            f"{self.attempt} – {self.question} – "
            f"{'correct' if self.is_correct else 'wrong'}"
        )


class QuizLevelProgress(models.Model):
    """
    Persistent progress for the 50-level
    standalone Quiz Challenge.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_level_progress",
    )
    level = models.PositiveIntegerField()
    difficulty = models.CharField(max_length=20)

    completed = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    best_score = models.PositiveIntegerField(default=0)
    best_percentage = models.PositiveIntegerField(default=0)

    stars = models.PositiveIntegerField(default=0)

    last_score = models.PositiveIntegerField(default=0)
    last_percentage = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "level"],
                name="unique_user_quiz_level_progress",
            ),
        ]
        indexes = [
            models.Index(
                fields=["user", "completed"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} – "
            f"Quiz Level {self.level}"
        )