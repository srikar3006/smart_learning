from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Groups rhymes such as animals, numbers and alphabets."""
    name = models.CharField(max_length=80, unique=True)
    icon_emoji = models.CharField(max_length=8, default="🎵")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Rhyme(models.Model):
    """A nursery rhyme lesson with optional video, audio and thumbnail media."""
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="rhymes")
    description = models.TextField(blank=True)
    lyrics = models.TextField(help_text="Lyrics displayed for the learner.")
    video_file = models.FileField(upload_to="rhymes/videos/", blank=True, null=True)
    external_video_url = models.URLField(
        blank=True,
        help_text="Optional embeddable video URL when a local upload is not used.",
    )
    audio_file = models.FileField(upload_to="rhymes/audio/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="rhymes/thumbnails/", blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(default=60)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="easy")
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__order", "order", "title"]
        indexes = [
            models.Index(fields=["is_published", "category"]),
            models.Index(fields=["difficulty", "is_published"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("rhymes:detail", kwargs={"slug": self.slug})

    @property
    def has_quiz(self):
        return hasattr(self, "quiz")

    @property
    def media_available(self):
        return bool(self.video_file or self.external_video_url or self.audio_file)

    def clean(self):
        if self.duration_seconds > 7200:
            raise ValidationError({"duration_seconds": "Lesson duration cannot exceed 2 hours."})
