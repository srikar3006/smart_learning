from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Platform account for a learner or a parent/guardian."""

    ACCOUNT_TYPE_CHOICES = [
        ("learner", "Learner"),
        ("parent", "Parent / Guardian"),
    ]

    AVATAR_CHOICES = [
        ("cat", "🐱 Cat"),
        ("dog", "🐶 Dog"),
        ("lion", "🦁 Lion"),
        ("monkey", "🐵 Monkey"),
        ("rabbit", "🐰 Rabbit"),
        ("panda", "🐼 Panda"),
        ("unicorn", "🦄 Unicorn"),
        ("star", "⭐ Star"),
    ]

    AGE_GROUP_CHOICES = [
        ("2-4", "2 – 4 years"),
        ("4-6", "4 – 6 years"),
        ("6-8", "6 – 8 years"),
    ]

    account_type = models.CharField(max_length=12, choices=ACCOUNT_TYPE_CHOICES, default="learner")
    avatar = models.CharField(max_length=20, choices=AVATAR_CHOICES, default="star")
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES, default="4-6", blank=True)
    parent_email = models.EmailField(blank=True, help_text="Parent/guardian email for learner updates.")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        limit_choices_to={"account_type": "parent"},
    )
    is_child_learner = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["first_name", "username"]

    def avatar_emoji(self):
        label = dict(self.AVATAR_CHOICES).get(self.avatar, "⭐ Star")
        return label.split(" ")[0]

    @property
    def is_parent(self):
        return self.account_type == "parent"

    @property
    def is_learner(self):
        return self.account_type == "learner"

    def __str__(self):
        return self.username
