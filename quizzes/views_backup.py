import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import learner_required
from progress.services import check_and_award_badges
from rhymes.models import Rhyme

from .models import (
    Choice,
    Question,
    Quiz,
    QuizAnswer,
    QuizAttempt,
    QuizLevelProgress,
)
from .level_data import CATEGORIES, LEVELS, get_level, stars_for_percentage


# ============================================================
# 50 LEVEL QUIZ CHALLENGE
# ============================================================

@learner_required
def quiz_dashboard(request):
    """Main 50-level Quiz Challenge page."""

    progress_rows = {
        p.level: p
        for p in QuizLevelProgress.objects.filter(user=request.user)
    }

    completed_levels = {
        level
        for level, row in progress_rows.items()
        if row.completed
    }

    # Find first incomplete level.
    unlocked_level = 1

    while unlocked_level < 50 and unlocked_level in completed_levels:
        unlocked_level += 1

    total_stars = sum(
        row.stars for row in progress_rows.values()
    )

    completed_count = len(completed_levels)

    current_level = min(unlocked_level, 50)

    display_levels = []

    for level in LEVELS:
        level_number = level["level"]
        row = progress_rows.get(level_number)

        display_levels.append(
            {
                **level,
                "unlocked": level_number <= unlocked_level,
                "completed": bool(row and row.completed),
                "best_percentage": (
                    row.best_percentage if row else 0
                ),
                "stars": row.stars if row else 0,
            }
        )

    current_config = get_level(current_level)

    return render(
        request,
        "quizzes/quiz_dashboard.html",
        {
            "levels": display_levels,
            "categories": CATEGORIES,
            "completed_count": completed_count,
            "total_stars": total_stars,
            "overall_percentage": round(
                completed_count / 50 * 100
            ),
            "current_level": current_level,
            "current_config": current_config,
        },
    )


def _level_is_unlocked(user, level_number):
    """
    Level 1 is always unlocked.
    Every other level requires the previous level to be completed.
    """

    if level_number == 1:
        return True

    return QuizLevelProgress.objects.filter(
        user=user,
        level=level_number - 1,
        completed=True,
    ).exists()


@learner_required
def quiz_level(request, level):
    """Display questions for one of the 50 challenge levels."""

    data = get_level(level)

    if not data:
        return redirect("quiz_challenge:dashboard")

    if not _level_is_unlocked(request.user, data["level"]):
        return redirect("quiz_challenge:dashboard")

    row = QuizLevelProgress.objects.filter(
        user=request.user,
        level=data["level"],
    ).first()

    return render(
        request,
        "quizzes/quiz_level.html",
        {
            "level_data": data,
            "level_progress": row,
            "questions_json": json.dumps(
                data["questions_data"]
            ),
        },
    )


@learner_required
def quiz_level_result(request, level):
    """Display the result page after completing a challenge level."""

    data = get_level(level)

    if not data:
        return redirect("quiz_challenge:dashboard")

    result = request.session.get(
        f"quiz_level_result_{data['level']}"
    )

    if not result:
        return redirect("quiz_challenge:dashboard")

    return render(
        request,
        "quizzes/quiz_level_result.html",
        {
            "level_data": data,
            "result": result,
        },
    )


@learner_required
@require_POST
def api_submit_level(request, level):
    """
    Receive answers from the 50-level quiz page.

    IMPORTANT:
    Answers are validated against the server-side level_data.
    Client-side JavaScript cannot decide the final score.
    """

    data = get_level(level)

    if not data:
        return JsonResponse(
            {
                "ok": False,
                "error": "That quiz level does not exist.",
            },
            status=404,
        )

    if not _level_is_unlocked(
        request.user,
        data["level"],
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": "Complete the previous level first.",
            },
            status=403,
        )

    try:
        payload = json.loads(
            request.body.decode("utf-8")
        )

        answers = payload.get("answers", {})

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid request body.",
            },
            status=400,
        )

    if not isinstance(answers, dict):
        return JsonResponse(
            {
                "ok": False,
                "error": "Answers must be an object.",
            },
            status=400,
        )

    correct = 0
    normalized = {}

    for question in data["questions_data"]:
        question_id = question["id"]

        chosen = str(
            answers.get(question_id, "")
        )

        normalized[question_id] = chosen

        if chosen == question["correctAnswer"]:
            correct += 1

    total = len(data["questions_data"])

    percentage = (
        round(correct / total * 100)
        if total
        else 0
    )

    stars = stars_for_percentage(
        percentage
    )

    # 60% or above = pass.
    passed = percentage >= 60

    with transaction.atomic():

        row, created = (
            QuizLevelProgress.objects
            .select_for_update()
            .get_or_create(
                user=request.user,
                level=data["level"],
                defaults={
                    "difficulty": data["difficulty"],
                },
            )
        )

        row.difficulty = data["difficulty"]

        row.attempts += 1

        row.last_score = correct
        row.last_percentage = percentage

        row.best_score = max(
            row.best_score,
            correct,
        )

        row.best_percentage = max(
            row.best_percentage,
            percentage,
        )

        row.stars = max(
            row.stars,
            stars,
        )

        if passed:
            row.completed = True

        row.save()

    result = {
        "score": correct,
        "total": total,
        "incorrect": total - correct,
        "percentage": percentage,
        "stars": stars,
        "best_stars": row.stars,
        "passed": passed,
        "level_completed": row.completed,
        "next_level": (
            data["level"] + 1
            if passed and data["level"] < 50
            else None
        ),
    }

    # Save result in session so result page can display it.
    request.session[
        f"quiz_level_result_{data['level']}"
    ] = result

    request.session.modified = True

    result_url = reverse(
        "quiz_challenge:level_result",
        kwargs={
            "level": data["level"],
        },
    )

    return JsonResponse(
        {
            "ok": True,
            **result,
            "result_url": result_url,
        }
    )


# ============================================================
# EXISTING RHYME QUIZ SYSTEM
# ============================================================

def _get_or_create_attempt(request, quiz):
    """
    Get the current unfinished rhyme quiz attempt,
    or create a new one.
    """

    session_key = f"quiz_attempt_{quiz.id}"

    attempt_id = request.session.get(
        session_key
    )

    attempt = None

    if attempt_id:

        attempt = QuizAttempt.objects.filter(
            id=attempt_id,
            user=request.user,
            quiz=quiz,
            completed_at__isnull=True,
        ).first()

    if attempt is None:

        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            total_questions=quiz.question_count,
        )

        request.session[session_key] = attempt.id

    return attempt


def _stars_for_percentage(pct):
    """Stars used by the existing rhyme quiz."""

    if pct >= 100:
        return 3

    if pct >= 80:
        return 2

    if pct >= 60:
        return 1

    return 0


@learner_required
def quiz_start(request, slug):
    """Start an existing rhyme quiz."""

    rhyme = get_object_or_404(
        Rhyme,
        slug=slug,
        is_published=True,
    )

    quiz = get_object_or_404(
        Quiz.objects.prefetch_related(
            "questions__choices"
        ),
        rhyme=rhyme,
    )

    if quiz.question_count == 0:

        return render(
            request,
            "quizzes/quiz_unavailable.html",
            {
                "rhyme": rhyme,
                "reason": (
                    "This quiz has not been configured yet."
                ),
            },
            status=503,
        )

    request.session.pop(
        f"quiz_attempt_{quiz.id}",
        None,
    )

    _get_or_create_attempt(
        request,
        quiz,
    )

    return redirect(
        "quizzes:question",
        slug=slug,
        order=1,
    )


@learner_required
def quiz_question(request, slug, order):
    """Display one question from an existing rhyme quiz."""

    rhyme = get_object_or_404(
        Rhyme,
        slug=slug,
        is_published=True,
    )

    quiz = get_object_or_404(
        Quiz,
        rhyme=rhyme,
    )

    attempt = _get_or_create_attempt(
        request,
        quiz,
    )

    questions = list(
        quiz.questions
        .prefetch_related("choices")
        .all()
    )

    if not questions:
        return redirect(
            "quizzes:start",
            slug=slug,
        )

    if order < 1 or order > len(questions):
        return redirect(
            "quizzes:result",
            slug=slug,
        )

    question = questions[order - 1]

    already_answered = (
        QuizAnswer.objects.filter(
            attempt=attempt,
            question=question,
        ).first()
    )

    return render(
        request,
        "quizzes/quiz_question.html",
        {
            "rhyme": rhyme,
            "quiz": quiz,
            "question": question,
            "order": order,
            "total": len(questions),
            "is_last": order == len(questions),
            "already_answered": already_answered,
        },
    )


@learner_required
@require_POST
def api_submit_answer(request, slug):
    """Submit one answer for an existing rhyme quiz."""

    try:
        payload = json.loads(
            request.body.decode("utf-8")
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": "Invalid request body.",
            },
            status=400,
        )

    rhyme = get_object_or_404(
        Rhyme,
        slug=slug,
        is_published=True,
    )

    quiz = get_object_or_404(
        Quiz,
        rhyme=rhyme,
    )

    attempt = _get_or_create_attempt(
        request,
        quiz,
    )

    if attempt.completed_at:

        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "This quiz attempt is already complete."
                ),
            },
            status=409,
        )

    try:

        question_id = int(
            payload.get("question_id")
        )

        choice_id = int(
            payload.get("choice_id")
        )

    except (
        TypeError,
        ValueError,
    ):

        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "Question and choice are required."
                ),
            },
            status=400,
        )

    question = get_object_or_404(
        Question,
        id=question_id,
        quiz=quiz,
    )

    choice = get_object_or_404(
        Choice,
        id=choice_id,
        question=question,
    )

    with transaction.atomic():

        answer, _ = (
            QuizAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    "choice": choice,
                    "is_correct": choice.is_correct,
                },
            )
        )

        score = (
            attempt.answers
            .filter(is_correct=True)
            .count()
        )

        attempt.score = score

        attempt.save(
            update_fields=["score"]
        )

    correct_choice = (
        question.choices
        .filter(is_correct=True)
        .first()
    )

    return JsonResponse(
        {
            "ok": True,
            "correct": choice.is_correct,
            "correct_choice_id": (
                correct_choice.id
                if correct_choice
                else None
            ),
            "running_score": score,
            "answered": attempt.answers.count(),
            "total": attempt.total_questions,
        }
    )


@learner_required
def quiz_result(request, slug):
    """Result page for the existing rhyme quiz."""

    rhyme = get_object_or_404(
        Rhyme,
        slug=slug,
        is_published=True,
    )

    quiz = get_object_or_404(
        Quiz,
        rhyme=rhyme,
    )

    attempt = _get_or_create_attempt(
        request,
        quiz,
    )

    answered_count = attempt.answers.count()

    if (
        answered_count < quiz.question_count
        and not attempt.completed_at
    ):

        unanswered = (
            quiz.questions
            .exclude(
                answers__attempt=attempt
            )
            .order_by("order")
            .first()
        )

        if unanswered:

            return redirect(
                "quizzes:question",
                slug=slug,
                order=unanswered.order,
            )

    if not attempt.completed_at:

        attempt.total_questions = (
            quiz.question_count
        )

        attempt.score = (
            attempt.answers
            .filter(is_correct=True)
            .count()
        )

        attempt.stars = _stars_for_percentage(
            attempt.score_pct
        )

        attempt.completed_at = timezone.now()

        attempt.save(
            update_fields=[
                "total_questions",
                "score",
                "stars",
                "completed_at",
            ]
        )

        request.session.pop(
            f"quiz_attempt_{quiz.id}",
            None,
        )

    new_badges = check_and_award_badges(
        request.user
    )

    return render(
        request,
        "quizzes/quiz_result.html",
        {
            "rhyme": rhyme,
            "quiz": quiz,
            "attempt": attempt,
            "passed": (
                attempt.score_pct
                >= quiz.passing_score_pct
            ),
            "new_badges": new_badges,
        },
    )