from django.db import transaction
from django.db.models import F, Sum

from quizzes.models import QuizAttempt
from .models import Badge, RhymeProgress, UserBadge


def get_progress_summary(user):
    rhyme_qs = RhymeProgress.objects.filter(user=user).select_related("rhyme", "rhyme__category")
    attempts = QuizAttempt.objects.filter(
        user=user,
        completed_at__isnull=False,
    ).select_related("quiz", "quiz__rhyme")

    completed_count = rhyme_qs.filter(completed=True).count()
    total_repeats = rhyme_qs.aggregate(total=Sum("repeat_count"))["total"] or 0
    quizzes_taken = attempts.count()
    perfect_scores = attempts.filter(score=F("total_questions")).exclude(total_questions=0).count()
    total_stars = attempts.aggregate(total=Sum("stars"))["total"] or 0

    avg_score_pct = 0
    if quizzes_taken:
        pct_sum = sum(attempt.score_pct for attempt in attempts)
        avg_score_pct = round(pct_sum / quizzes_taken)

    return {
        "rhyme_progress": rhyme_qs.order_by("-last_played", "rhyme__title"),
        "completed_count": completed_count,
        "total_repeats": total_repeats,
        "quizzes_taken": quizzes_taken,
        "perfect_scores": perfect_scores,
        "total_stars": total_stars,
        "avg_score_pct": avg_score_pct,
        "quiz_attempts": attempts.order_by("-completed_at")[:10],
        "badges": UserBadge.objects.filter(user=user).select_related("badge"),
    }


@transaction.atomic
def check_and_award_badges(user):
    """Evaluate the documented rule-based badges after a progress event."""
    summary = get_progress_summary(user)
    metrics = {
        "rhymes_completed": summary["completed_count"],
        "quiz_score_perfect": summary["perfect_scores"],
        "repeat_master": summary["total_repeats"],
        "quizzes_taken": summary["quizzes_taken"],
    }

    existing = set(UserBadge.objects.filter(user=user).values_list("badge_id", flat=True))
    newly_awarded = []

    for badge in Badge.objects.exclude(id__in=existing).order_by("id"):
        if metrics.get(badge.criteria_type, 0) >= badge.criteria_value:
            UserBadge.objects.get_or_create(user=user, badge=badge)
            newly_awarded.append(badge)

    return newly_awarded
