
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


RHYMES_PAGE_SHOWCASE = [
    {
        "title": "Humpty Dumpty",
        "category": "Nursery",
        "category_icon": "🥚",
        "description": "A classic rhyme about Humpty’s big tumble.",
        "rating": "4.8",
        "duration": "02:15",
        "video_id": "nrv495corBc",
        "difficulty": "Easy",
        "color": "violet",
        "fallback_image": "img/rhymes/humpty.svg",
    },
    {
        "title": "Twinkle Twinkle Little Star",
        "category": "Nature",
        "category_icon": "⭐",
        "description": "A gentle lullaby about a shining little star.",
        "rating": "4.9",
        "duration": "01:45",
        "video_id": "yCjJyiqpAuU",
        "difficulty": "Easy",
        "color": "indigo",
        "fallback_image": "img/rhymes/twinkle.svg",
    },
    {
        "title": "Baa Baa Black Sheep",
        "category": "Animals",
        "category_icon": "🐑",
        "description": "Sing along with a friendly black sheep on the farm.",
        "rating": "4.7",
        "duration": "01:30",
        "video_id": "g7c3G4m2BRA",
        "difficulty": "Easy",
        "color": "green",
        "fallback_image": "img/rhymes/baa-baa.svg",
    },
    {
        "title": "Wheels on the Bus",
        "category": "Action",
        "category_icon": "🚌",
        "description": "Ride along and move with the wheels, doors and wipers.",
        "rating": "4.6",
        "duration": "02:05",
        "video_id": "IRap6FOoZKA",
        "difficulty": "Easy",
        "color": "blue",
        "fallback_image": "img/rhymes/wheels.svg",
    },
    {
        "title": "Mary Had a Little Lamb",
        "category": "Animals",
        "category_icon": "🐑",
        "description": "A sweet farm rhyme featuring a little lamb and friends.",
        "rating": "4.7",
        "duration": "01:50",
        "video_id": "28W4ywSsBPc",
        "difficulty": "Easy",
        "color": "rose",
        "fallback_image": "img/rhymes/mary.svg",
    },
    {
        "title": "Rain Rain Go Away",
        "category": "Nature",
        "category_icon": "🌧️",
        "description": "A cheerful rainy-day song for family sing-along time.",
        "rating": "4.5",
        "duration": "01:40",
        "video_id": "LFrKYjrIDs8",
        "difficulty": "Easy",
        "color": "sky",
        "fallback_image": "img/rhymes/rain.svg",
    },
    {
        "title": "If You're Happy and You Know It",
        "category": "Action",
        "category_icon": "👏",
        "description": "Clap, stomp and shout hooray in this movement rhyme.",
        "rating": "4.8",
        "duration": "01:55",
        "video_id": "M6LoRZsHMSs",
        "difficulty": "Easy",
        "color": "yellow",
        "fallback_image": "img/rhymes/happy.svg",
    },
    {
        "title": "Jingle Bells",
        "category": "Festival",
        "category_icon": "🎄",
        "description": "Dash through the snow with a bright holiday sing-along.",
        "rating": "4.9",
        "duration": "02:10",
        "video_id": "4YBGRGBj7_w",
        "difficulty": "Easy",
        "color": "red",
        "fallback_image": "img/rhymes/jingle.svg",
    },
]


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
            "showcase_rhymes": RHYMES_PAGE_SHOWCASE,
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
