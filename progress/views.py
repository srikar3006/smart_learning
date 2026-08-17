from django.http import JsonResponse
from django.shortcuts import render

from accounts.decorators import learner_required
from .services import get_progress_summary


@learner_required
def progress_dashboard(request):
    if request.user.is_parent:
        from django.shortcuts import redirect
        return redirect("parent:dashboard")

    return render(request, "progress/progress.html", get_progress_summary(request.user))


@learner_required
def api_progress_summary(request):
    if request.user.is_parent:
        return JsonResponse({"ok": False, "error": "Learner progress endpoint only."}, status=403)

    summary = get_progress_summary(request.user)
    return JsonResponse(
        {
            "ok": True,
            "completed_count": summary["completed_count"],
            "total_repeats": summary["total_repeats"],
            "quizzes_taken": summary["quizzes_taken"],
            "perfect_scores": summary["perfect_scores"],
            "total_stars": summary["total_stars"],
            "avg_score_pct": summary["avg_score_pct"],
            "badge_count": summary["badges"].count(),
        }
    )
