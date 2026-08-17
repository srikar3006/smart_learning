import json
from urllib.parse import urlparse

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from accounts.decorators import learner_required
from progress.models import RhymeProgress
from progress.services import check_and_award_badges
from .models import Category, Rhyme


def _safe_embed_url(url):
    """Normalize common YouTube links; otherwise return the configured URL."""
    if not url:
        return ""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if "youtube.com" in host and parsed.path == "/watch":
        video_id = parsed.query.split("v=", 1)[-1].split("&", 1)[0]
        return f"https://www.youtube.com/embed/{video_id}" if video_id else url
    if "youtu.be" in host:
        video_id = parsed.path.strip("/").split("/", 1)[0]
        return f"https://www.youtube.com/embed/{video_id}" if video_id else url
    return url


@learner_required
def rhyme_list(request):
    categories = Category.objects.prefetch_related("rhymes").all()
    selected_category_id = request.GET.get("category")
    search = request.GET.get("q", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()

    rhymes = Rhyme.objects.filter(is_published=True).select_related("category")
    if selected_category_id and selected_category_id.isdigit():
        rhymes = rhymes.filter(category_id=int(selected_category_id))
    if search:
        rhymes = rhymes.filter(Q(title__icontains=search) | Q(description__icontains=search))
    if difficulty in {"easy", "medium", "hard"}:
        rhymes = rhymes.filter(difficulty=difficulty)

    completed_ids = set(
        RhymeProgress.objects.filter(user=request.user, completed=True).values_list("rhyme_id", flat=True)
    )

    return render(
        request,
        "rhymes/rhyme_list.html",
        {
            "categories": categories,
            "rhymes": rhymes,
            "selected_category_id": int(selected_category_id) if selected_category_id and selected_category_id.isdigit() else None,
            "search": search,
            "difficulty": difficulty,
            "completed_ids": completed_ids,
        },
    )


@learner_required
def rhyme_detail(request, slug):
    rhyme = get_object_or_404(Rhyme.objects.select_related("category"), slug=slug, is_published=True)
    progress, _ = RhymeProgress.objects.get_or_create(user=request.user, rhyme=rhyme)
    return render(
        request,
        "rhymes/rhyme_detail.html",
        {
            "rhyme": rhyme,
            "progress": progress,
            "embed_url": _safe_embed_url(rhyme.external_video_url),
        },
    )


def _register_play_for_user(user, rhyme):
    progress, _ = RhymeProgress.objects.get_or_create(user=user, rhyme=rhyme)
    progress.register_play()
    return progress, check_and_award_badges(user)


@learner_required
@require_POST
def api_log_play(request, slug):
    rhyme = get_object_or_404(Rhyme, slug=slug, is_published=True)
    progress, new_badges = _register_play_for_user(request.user, rhyme)
    return JsonResponse(
        {
            "ok": True,
            "times_played": progress.times_played,
            "completed": progress.completed,
            "new_badges": [badge.name for badge in new_badges],
        }
    )


@learner_required
@require_POST
def api_log_repeat(request, slug):
    rhyme = get_object_or_404(Rhyme, slug=slug, is_published=True)
    progress, _ = RhymeProgress.objects.get_or_create(user=request.user, rhyme=rhyme)
    progress.register_repeat()
    new_badges = check_and_award_badges(request.user)
    return JsonResponse(
        {
            "ok": True,
            "repeat_count": progress.repeat_count,
            "new_badges": [badge.name for badge in new_badges],
        }
    )


@learner_required
@require_POST
def api_mark_complete(request, slug):
    rhyme = get_object_or_404(Rhyme, slug=slug, is_published=True)
    progress, _ = RhymeProgress.objects.get_or_create(user=request.user, rhyme=rhyme)
    if not progress.completed:
        progress.completed = True
        from django.utils import timezone
        progress.first_completed_at = timezone.now()
    progress.last_played = timezone.now()
    progress.save(update_fields=["completed", "first_completed_at", "last_played"])
    new_badges = check_and_award_badges(request.user)
    return JsonResponse(
        {
            "ok": True,
            "completed": progress.completed,
            "new_badges": [badge.name for badge in new_badges],
        }
    )
