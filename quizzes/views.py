import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import learner_required
from progress.services import check_and_award_badges
from rhymes.models import Rhyme

from .models import Choice, Question, Quiz, QuizAnswer, QuizAttempt


def _get_or_create_attempt(request, quiz):
    session_key = f"quiz_attempt_{quiz.id}"
    attempt_id = request.session.get(session_key)
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
    if pct >= 100:
        return 3
    if pct >= 80:
        return 2
    if pct >= 60:
        return 1
    return 0


@learner_required
def quiz_start(request, slug):
    rhyme = get_object_or_404(Rhyme, slug=slug, is_published=True)
    quiz = get_object_or_404(Quiz.objects.prefetch_related("questions__choices"), rhyme=rhyme)

    if quiz.question_count == 0:
        return render(
            request,
            "quizzes/quiz_unavailable.html",
            {"rhyme": rhyme, "reason": "This quiz has not been configured yet."},
            status=503,
        )

    request.session.pop(f"quiz_attempt_{quiz.id}", None)
    _get_or_create_attempt(request, quiz)
    return redirect("quizzes:question", slug=slug, order=1)


@learner_required
def quiz_question(request, slug, order):
    rhyme = get_object_or_404(Rhyme, slug=slug, is_published=True)
    quiz = get_object_or_404(Quiz, rhyme=rhyme)
    attempt = _get_or_create_attempt(request, quiz)
    questions = list(quiz.questions.prefetch_related("choices").all())

    if not questions:
        return redirect("quizzes:start", slug=slug)
    if order < 1 or order > len(questions):
        return redirect("quizzes:result", slug=slug)

    question = questions[order - 1]
    already_answered = QuizAnswer.objects.filter(attempt=attempt, question=question).first()

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
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid request body."}, status=400)

    rhyme = get_object_or_404(Rhyme, slug=slug, is_published=True)
    quiz = get_object_or_404(Quiz, rhyme=rhyme)
    attempt = _get_or_create_attempt(request, quiz)

    if attempt.completed_at:
        return JsonResponse({"ok": False, "error": "This quiz attempt is already complete."}, status=409)

    try:
        question_id = int(payload.get("question_id"))
        choice_id = int(payload.get("choice_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Question and choice are required."}, status=400)

    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    choice = get_object_or_404(Choice, id=choice_id, question=question)

    with transaction.atomic():
        answer, _ = QuizAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={"choice": choice, "is_correct": choice.is_correct},
        )
        score = attempt.answers.filter(is_correct=True).count()
        attempt.score = score
        attempt.save(update_fields=["score"])

    correct_choice = question.choices.filter(is_correct=True).first()
    return JsonResponse(
        {
            "ok": True,
            "correct": choice.is_correct,
            "correct_choice_id": correct_choice.id if correct_choice else None,
            "running_score": score,
            "answered": attempt.answers.count(),
            "total": attempt.total_questions,
        }
    )


@learner_required
def quiz_result(request, slug):
    rhyme = get_object_or_404(Rhyme, slug=slug, is_published=True)
    quiz = get_object_or_404(Quiz, rhyme=rhyme)
    attempt = _get_or_create_attempt(request, quiz)
    answered_count = attempt.answers.count()

    if answered_count < quiz.question_count and not attempt.completed_at:
        unanswered = quiz.questions.exclude(answers__attempt=attempt).order_by("order").first()
        if unanswered:
            return redirect("quizzes:question", slug=slug, order=unanswered.order)

    if not attempt.completed_at:
        attempt.total_questions = quiz.question_count
        attempt.score = attempt.answers.filter(is_correct=True).count()
        attempt.stars = _stars_for_percentage(attempt.score_pct)
        attempt.completed_at = timezone.now()
        attempt.save(
            update_fields=["total_questions", "score", "stars", "completed_at"]
        )
        request.session.pop(f"quiz_attempt_{quiz.id}", None)

    new_badges = check_and_award_badges(request.user)

    return render(
        request,
        "quizzes/quiz_result.html",
        {
            "rhyme": rhyme,
            "quiz": quiz,
            "attempt": attempt,
            "passed": attempt.score_pct >= quiz.passing_score_pct,
            "new_badges": new_badges,
        },
    )
