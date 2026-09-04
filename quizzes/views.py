import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .level_data import CATEGORIES, LEVELS, get_level, stars_for_percentage
from accounts.decorators import learner_required
from rhymes.models import Rhyme

from .models import Choice, Quiz, QuizAnswer, QuizAttempt, Question, QuizLevelProgress


# ============================================================
# QUIZ CHALLENGE — STANDALONE 10-LEVEL SYSTEM
# ============================================================


def _level_is_unlocked(user, level_number):
    if level_number == 1:
        return True
    return QuizLevelProgress.objects.filter(
        user=user,
        level=level_number - 1,
        completed=True,
    ).exists()


@learner_required
def quiz_dashboard(request):
    progress_rows = {
        row.level: row
        for row in QuizLevelProgress.objects.filter(
            user=request.user,
            level__gte=1,
            level__lte=10,
        )
    }

    completed_count = sum(
        1 for row in progress_rows.values() if row.completed
    )
    total_stars = sum(row.stars for row in progress_rows.values())
    unlocked_level = 1
    while unlocked_level < 10 and progress_rows.get(unlocked_level, None) and progress_rows[unlocked_level].completed:
        unlocked_level += 1

    current_level = unlocked_level
    display_levels = []
    for level in LEVELS:
        number = level["level"]
        row = progress_rows.get(number)
        categories_for_filter = sorted({q["category"] for q in level["questions_data"]})
        display_levels.append({
            **level,
            "unlocked": number <= unlocked_level,
            "completed": bool(row and row.completed),
            "best_percentage": row.best_percentage if row else 0,
            "stars": row.stars if row else 0,
            "categories_for_filter": categories_for_filter,
        })

    attempts_played = sum(row.attempts for row in progress_rows.values())
    best_score = max((row.best_percentage for row in progress_rows.values()), default=0)
    category_progress = {category["name"]: completed_count for category in CATEGORIES}
    current_config = get_level(current_level)

    return render(request, "quizzes/quiz_dashboard.html", {
        "levels": display_levels,
        "categories": CATEGORIES,
        "completed_count": completed_count,
        "total_stars": total_stars,
        "overall_percentage": round(completed_count / 10 * 100),
        "current_level": current_level,
        "current_config": current_config,
        "attempts_played": attempts_played,
        "best_score": best_score,
        "category_progress": category_progress,
    })


@learner_required
def quiz_level(request, level):
    data = get_level(level)
    if not data or not _level_is_unlocked(request.user, data["level"]):
        return redirect("quiz_challenge:dashboard")

    row = QuizLevelProgress.objects.filter(
        user=request.user,
        level=data["level"],
    ).first()

    return render(request, "quizzes/quiz_level.html", {
        "level_data": data,
        "level_progress": row,
        "questions_json": json.dumps(data["questions_data"]),
        "restart": request.GET.get("restart") == "1",
    })


@learner_required
def quiz_level_result(request, level):
    data = get_level(level)
    if not data:
        return redirect("quiz_challenge:dashboard")

    result = request.session.get(f"quiz_level_result_{data['level']}")
    if not result:
        return redirect("quiz_challenge:dashboard")

    return render(request, "quizzes/quiz_level_result.html", {
        "level_data": data,
        "result": result,
    })


@learner_required
@require_POST
def api_submit_level(request, level):
    """Validate the complete level server-side and persist real progress."""
    data = get_level(level)
    if not data:
        return JsonResponse({"ok": False, "error": "That quiz level does not exist."}, status=404)
    if not _level_is_unlocked(request.user, data["level"]):
        return JsonResponse({"ok": False, "error": "Complete the previous level first."}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid request body."}, status=400)

    answers = payload.get("answers", {})
    if not isinstance(answers, dict):
        return JsonResponse({"ok": False, "error": "Answers must be an object."}, status=400)

    # Category filtering is a presentation/filter feature only. A completed level
    # is always scored against all questions so the unlock rule cannot be bypassed.
    correct = 0
    for question in data["questions_data"]:
        if str(answers.get(question["id"], "")) == question["correctAnswer"]:
            correct += 1

    total = len(data["questions_data"])
    percentage = round(correct / total * 100) if total else 0
    stars = stars_for_percentage(percentage)
    passed = percentage >= 60

    with transaction.atomic():
        row, _ = QuizLevelProgress.objects.select_for_update().get_or_create(
            user=request.user,
            level=data["level"],
            defaults={"difficulty": data["difficulty"]},
        )
        row.difficulty = data["difficulty"]
        row.attempts += 1
        row.last_score = correct
        row.last_percentage = percentage
        row.best_score = max(row.best_score, correct)
        row.best_percentage = max(row.best_percentage, percentage)
        row.stars = max(row.stars, stars)
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
        "next_level": data["level"] + 1 if passed and data["level"] < 10 else None,
    }
    request.session[f"quiz_level_result_{data['level']}"] = result
    request.session.modified = True

    return JsonResponse({
        "ok": True,
        **result,
        "result_url": reverse("quiz_challenge:level_result", kwargs={"level": data["level"]}),
    })


@learner_required
def quiz_list(request):
    """
    Display all published quizzes available to the learner.
    """
    quizzes = (
        Quiz.objects
        .select_related("rhyme", "rhyme__category")
        .prefetch_related("questions")
        .filter(rhyme__is_published=True)
        .order_by(
            "rhyme__category__order",
            "rhyme__order",
            "title",
        )
    )

    return render(
        request,
        "quizzes/quiz_list.html",
        {
            "quizzes": quizzes,
        },
    )


@learner_required
def quiz_start(request, slug):
    """
    Start a new quiz attempt.
    """
    rhyme = get_object_or_404(
        Rhyme,
        slug=slug,
        is_published=True,
    )

    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__choices"),
        rhyme=rhyme,
    )

    questions = quiz.questions.all().order_by("order")

    if not questions.exists():
        return render(
            request,
            "quizzes/quiz_list.html",
            {
                "quizzes": Quiz.objects.filter(
                    rhyme__is_published=True
                ).select_related(
                    "rhyme",
                    "rhyme__category",
                ),
                "error": "This quiz does not have any questions yet.",
            },
        )

    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
    )

    return redirect(
        "quizzes:question",
        slug=slug,
        order=questions.first().order,
    )


@learner_required
def quiz_question(request, slug, order):
    """
    Display a quiz question.
    """
    rhyme = get_object_or_404(
        Rhyme,
        slug=slug,
        is_published=True,
    )

    quiz = get_object_or_404(
        Quiz.objects.select_related("rhyme"),
        rhyme=rhyme,
    )

    question = get_object_or_404(
        Question.objects.prefetch_related("choices"),
        quiz=quiz,
        order=order,
    )

    attempt = (
        QuizAttempt.objects
        .filter(
            user=request.user,
            quiz=quiz,
        )
        .order_by("-started_at")
        .first()
    )

    if attempt is None:
        return redirect(
            "quizzes:start",
            slug=slug,
        )

    questions = list(
        quiz.questions.all().order_by("order")
    )

    current_index = next(
        (
            index
            for index, item in enumerate(questions)
            if item.pk == question.pk
        ),
        0,
    )

    total_questions = len(questions)

    return render(
        request,
        "quizzes/question.html",
        {
            "quiz": quiz,
            "question": question,
            "attempt": attempt,
            "current_index": current_index + 1,
            "total_questions": total_questions,
            "progress_percent": (
                int(((current_index + 1) / total_questions) * 100)
                if total_questions
                else 0
            ),
        },
    )


@learner_required
@require_POST
def api_submit_answer(request, slug):
    """
    Submit an answer for the current quiz question.
    """
    rhyme = get_object_or_404(
        Rhyme,
        slug=slug,
        is_published=True,
    )

    quiz = get_object_or_404(
        Quiz,
        rhyme=rhyme,
    )

    attempt = (
        QuizAttempt.objects
        .filter(
            user=request.user,
            quiz=quiz,
        )
        .order_by("-started_at")
        .first()
    )

    if attempt is None:
        return JsonResponse(
            {
                "success": False,
                "error": "Quiz attempt not found.",
            },
            status=404,
        )

    if hasattr(attempt, "completed") and attempt.completed:
        return JsonResponse(
            {
                "success": False,
                "error": "This quiz has already been completed.",
            },
            status=400,
        )

    question_id = request.POST.get("question_id")
    choice_id = request.POST.get("choice_id")

    if not question_id or not choice_id:
        return JsonResponse(
            {
                "success": False,
                "error": "Question and choice are required.",
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

    answer, created = QuizAnswer.objects.update_or_create(
        attempt=attempt,
        question=question,
        defaults={
            "choice": choice,
            "is_correct": choice.is_correct,
        },
    )

    questions = list(
        quiz.questions.all().order_by("order")
    )

    current_index = next(
        (
            index
            for index, item in enumerate(questions)
            if item.pk == question.pk
        ),
        0,
    )

    is_last_question = (
        current_index >= len(questions) - 1
    )

    if is_last_question:
        return JsonResponse(
            {
                "success": True,
                "is_last_question": True,
                "next_url": (
                    f"/quizzes/{quiz.rhyme.slug}/result/"
                ),
                "is_correct": choice.is_correct,
            }
        )

    next_question = questions[current_index + 1]

    return JsonResponse(
        {
            "success": True,
            "is_last_question": False,
            "next_url": (
                f"/quizzes/{quiz.rhyme.slug}/question/"
                f"{next_question.order}/"
            ),
            "is_correct": choice.is_correct,
        }
    )


@learner_required
def quiz_result(request, slug):
    """
    Display the final quiz result.
    """
    rhyme = get_object_or_404(
        Rhyme,
        slug=slug,
        is_published=True,
    )

    quiz = get_object_or_404(
        Quiz,
        rhyme=rhyme,
    )

    attempt = (
        QuizAttempt.objects
        .filter(
            user=request.user,
            quiz=quiz,
        )
        .order_by("-started_at")
        .first()
    )

    if attempt is None:
        return redirect(
            "quizzes:start",
            slug=slug,
        )

    answers = QuizAnswer.objects.filter(
        attempt=attempt
    ).select_related(
        "question",
        "choice",
    )

    total_questions = quiz.questions.count()
    correct_answers = answers.filter(
        is_correct=True
    ).count()

    score_percentage = (
        round(
            (correct_answers / total_questions) * 100
        )
        if total_questions
        else 0
    )

    passed = (
        score_percentage >= quiz.passing_score_pct
    )

    return render(
        request,
        "quizzes/result.html",
        {
            "quiz": quiz,
            "attempt": attempt,
            "answers": answers,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score_percentage": score_percentage,
            "passed": passed,
        },
    )