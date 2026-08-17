from django.conf import settings
from django.db import models
from django.utils import timezone

from rhymes.models import Rhyme


class RhymeProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rhyme_progress")
    rhyme = models.ForeignKey(Rhyme, on_delete=models.CASCADE, related_name="progress_records")
    times_played = models.PositiveIntegerField(default=0)
    repeat_count = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    last_played = models.DateTimeField(null=True, blank=True)
    first_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "rhyme"], name="unique_user_rhyme_progress"),
        ]
        indexes = [
            models.Index(fields=["user", "completed"]),
            models.Index(fields=["user", "last_played"]),
        ]

    def __str__(self):
        return f"{self.user.username} – {self.rhyme.title}"

    def register_play(self):
        now = timezone.now()
        self.times_played += 1
        self.last_played = now
        if not self.completed:
            self.completed = True
            self.first_completed_at = now
        self.save(update_fields=["times_played", "last_played", "completed", "first_completed_at"])

    def register_repeat(self):
        self.repeat_count += 1
        self.last_played = timezone.now()
        self.save(update_fields=["repeat_count", "last_played"])


class Badge(models.Model):
    CRITERIA_CHOICES = [
        ("rhymes_completed", "Number of rhymes completed"),
        ("quiz_score_perfect", "Number of perfect quiz scores"),
        ("repeat_master", "Total repeat plays across all rhymes"),
        ("quizzes_taken", "Number of quizzes completed"),
    ]

    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=200)
    icon_emoji = models.CharField(max_length=8, default="🏅")
    criteria_type = models.CharField(max_length=30, choices=CRITERIA_CHOICES)
    criteria_value = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awarded_to")
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "badge"], name="unique_user_badge"),
        ]
        ordering = ["-earned_at"]

    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"
