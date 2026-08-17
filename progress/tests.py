from django.test import TestCase

from accounts.models import User
from rhymes.models import Category, Rhyme
from .models import RhymeProgress
from .services import get_progress_summary


class ProgressTests(TestCase):
    def test_summary_counts_completed_rhymes(self):
        user = User.objects.create_user(
            username="progresslearner",
            password="StrongPass123!",
            account_type="learner",
        )
        category = Category.objects.create(name="Test", icon_emoji="🎵")
        rhyme = Rhyme.objects.create(
            title="Test Rhyme",
            slug="test-rhyme",
            category=category,
            lyrics="Test",
        )
        progress = RhymeProgress.objects.create(user=user, rhyme=rhyme)
        progress.register_play()
        progress.register_repeat()
        summary = get_progress_summary(user)
        self.assertEqual(summary["completed_count"], 1)
        self.assertEqual(summary["total_repeats"], 1)
