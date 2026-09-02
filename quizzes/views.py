from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import learner_required
from rhymes.models import Rhyme

from .models import Choice, Quiz, QuizAnswer, QuizAttempt, Question


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