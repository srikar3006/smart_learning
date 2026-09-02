

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from django.db.models import Count, Q, Sum

from django.shortcuts import redirect, render

from django.templatetags.static import static

from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from accounts.decorators import parent_required, learner_required
from accounts.models import User

from accounts.forms import ChildCreationForm

from .video_data import CATEGORIES, VIDEOS

from progress.services import get_progress_summary
from progress.models import RhymeProgress, UserBadge

from quizzes.models import Quiz, QuizAttempt

from rhymes.models import Category, Rhyme


# ============================================================
# LANDING PAGE
# ============================================================

def landing(request):
    """
    Smart Learning Welcome Page.

    IMPORTANT:

    The landing page is public.

    It does NOT automatically redirect authenticated users
    to Home.

    Therefore:

        Open Project
              ↓
        Welcome Page
              ↓
        User clicks Login
              ↓
        Login Page
    """

    return render(
        request,
        "core/landing.html"
    )


# ============================================================
# HOME / LEARNER DASHBOARD
# ============================================================

@never_cache
@login_required(
    login_url="accounts:login"
)
def home(request):
    """
    Protected Smart Learning Home.

    A user must have a valid Django authenticated session.

    If the user:

        - is not logged in
        - has logged out
        - has an invalid session
        - has an expired session

    Django redirects them to Login.
    """

    # ========================================================
    # PARENT ACCOUNT
    # ========================================================

    if request.user.is_parent:

        return redirect(
            "parent:dashboard"
        )

    # ========================================================
    # CATEGORIES
    # ========================================================

    categories = list(
        Category.objects
        .prefetch_related("rhymes")
        .all()[:6]
    )

    # ========================================================
    # CONTINUE LEARNING
    # ========================================================

    continue_learning = (

        Rhyme.objects.filter(

            is_published=True,

            progress_records__user=request.user,

            progress_records__completed=False,

        )

        .select_related(
            "category"
        )

        .distinct()[:4]
    )

    # ========================================================
    # PROGRESS SUMMARY
    # ========================================================

    summary = get_progress_summary(
        request.user
    )

    # ========================================================
    # FEATURED RHYMES
    # ========================================================

    featured = list(

        Rhyme.objects.filter(
            is_published=True
        )

        .select_related(
            "category"
        )[:4]
    )

    # ========================================================
    # TEMPLATE CONTEXT
    # ========================================================

    context = {

        "categories":
            categories,

        "continue_learning":
            continue_learning,

        "featured":
            featured,

        "summary":
            summary,
    }

    # ========================================================
    # RENDER HOME
    # ========================================================

    return render(
        request,
        "core/home.html",
        context
    )


# ============================================================
# ANIMATED VIDEOS & STORIES
# ============================================================
#
# Content (categories + video/story list) lives in
# core/video_data.py — edit that file to add new videos.
# Search, category filtering, the video player, "Keep Watching",
# "My List" and "History" all run client-side (see
# templates/core/videos.html) so this view just supplies the
# base data set.
# ============================================================

@never_cache
@learner_required
def videos(request):

    # Resolve each video/thumbnail path through Django's static()
    # helper here, once, so the template/JS can use them directly
    # without needing to know STATIC_URL.
    videos_for_js = [
        {
            **item,
            "thumbnail": static(item["thumbnail"]),
            "video": static(item["video"]),
        }
        for item in VIDEOS
    ]

    return render(

        request,

        "core/videos.html",

        {
            "categories":
                CATEGORIES,

            "videos":
                VIDEOS,

            "videos_json":
                videos_for_js,
        },
    )


# ============================================================
# PARENT DASHBOARD
# ============================================================

@parent_required
def parent_dashboard(request):

    children = list(

        request.user.children

        .filter(
            is_active=True
        )

        .annotate(

            completed_rhymes=Count(

                "rhyme_progress",

                filter=Q(
                    rhyme_progress__completed=True
                ),

                distinct=True,
            ),

            quizzes_completed=Count(

                "quiz_attempts",

                filter=Q(
                    quiz_attempts__completed_at__isnull=False
                ),

                distinct=True,
            ),
        )
    )

    # ========================================================
    # SELECTED CHILD
    # ========================================================

    selected_child = None

    selected_child_id = request.GET.get(
        "child"
    )

    if selected_child_id:

        selected_child = next(

            (
                child

                for child in children

                if str(child.id)
                == str(selected_child_id)
            ),

            None,
        )

    # ========================================================
    # DEFAULT CHILD
    # ========================================================

    if (
        not selected_child
        and children
    ):

        selected_child = children[0]

    # ========================================================
    # CHILD PROGRESS
    # ========================================================

    child_summary = (

        get_progress_summary(
            selected_child
        )

        if selected_child

        else None
    )

    # ========================================================
    # RECENT QUIZ ATTEMPTS
    # ========================================================

    recent_attempts = (

        QuizAttempt.objects.filter(

            user__parent=request.user,

            completed_at__isnull=False,

        )

        .select_related(

            "user",

            "quiz",

            "quiz__rhyme",

        )

        .order_by(
            "-completed_at"
        )[:8]
    )

    # ========================================================
    # RENDER PARENT DASHBOARD
    # ========================================================

    return render(

        request,

        "core/parent_dashboard.html",

        {
            "children":
                children,

            "selected_child":
                selected_child,

            "child_summary":
                child_summary,

            "recent_attempts":
                recent_attempts,
        },
    )


# ============================================================
# ADD CHILD
# ============================================================

@parent_required
def add_child(request):

    if request.method == "POST":

        form = ChildCreationForm(

            request.POST,

            parent=request.user,
        )

        if form.is_valid():

            child = form.save()

            from django.contrib import messages

            messages.success(

                request,

                f"{child.first_name or child.username} "
                "was added to your family space. 🎉",
            )

            return redirect(
                "parent:dashboard"
            )

    else:

        form = ChildCreationForm(
            parent=request.user
        )

    return render(

        request,

        "core/add_child.html",

        {
            "form":
                form
        },
    )


# ============================================================
# LEARNER PROFILE
# ============================================================

PROFILE_INTERESTS = [
    ("animals", "🦁", "Animals"),
    ("music", "🎵", "Music"),
    ("stories", "📖", "Stories"),
    ("puzzles", "🧩", "Puzzles"),
    ("colors", "🎨", "Colors"),
]


@never_cache
@login_required(login_url="accounts:login")
@require_http_methods(["GET", "POST"])
def profile(request):
    if request.user.is_parent:
        return redirect("parent:dashboard")

    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", "").strip()
        avatar = request.POST.get("avatar", user.avatar)
        age_group = request.POST.get("age_group", user.age_group)

        valid_avatars = {value for value, _ in user.AVATAR_CHOICES}
        valid_age_groups = {value for value, _ in user.AGE_GROUP_CHOICES}
        if avatar in valid_avatars:
            user.avatar = avatar
        if age_group in valid_age_groups:
            user.age_group = age_group

        user.interests = [
            value for value, _, _ in PROFILE_INTERESTS
            if value in request.POST.getlist("interests")
        ]
        user.save(update_fields=["first_name", "avatar", "age_group", "interests"])
        messages.success(request, "Your profile was updated successfully. ✨")
        return redirect("core:profile")

    rhyme_progress = list(
        RhymeProgress.objects.filter(user=user)
        .select_related("rhyme", "rhyme__category")
        .order_by("-last_played", "-first_completed_at")
    )
    completed_rhymes = sum(1 for item in rhyme_progress if item.completed)

    from rhymes.models import Rhyme
    total_rhymes = Rhyme.objects.filter(is_published=True).count()

    quiz_attempts = list(
        QuizAttempt.objects.filter(user=user, completed_at__isnull=False)
        .select_related("quiz", "quiz__rhyme")
        .order_by("-completed_at")
    )
    quizzes_completed = len(quiz_attempts)
    total_quizzes = Quiz.objects.count()

    badges = list(
        UserBadge.objects.filter(user=user)
        .select_related("badge")
        .order_by("-earned_at")
    )

    total_stars = QuizAttempt.objects.filter(
        user=user, completed_at__isnull=False
    ).aggregate(total=Sum("stars"))["total"] or 0

    activities = []
    for item in rhyme_progress:
        if item.last_played:
            activities.append({
                "icon": "🎵",
                "title": f"Watched: {item.rhyme.title}",
                "description": "Rhyme",
                "when": item.last_played,
            })
    for attempt in quiz_attempts:
        activities.append({
            "icon": "🏆",
            "title": f"Completed Quiz: {attempt.quiz.title}",
            "description": f"Score {attempt.score}/{attempt.total_questions}",
            "when": attempt.completed_at,
        })
    activities.sort(key=lambda item: item["when"], reverse=True)
    activities = activities[:8]

    level = max(1, min(10, 1 + (completed_rhymes + quizzes_completed) // 5))

    return render(
        request,
        "core/profile.html",
        {
            "profile_user": user,
            "activities": activities,
            "badges": badges,
            "interests": PROFILE_INTERESTS,
            "selected_interests": set(user.interests or []),
            "videos": VIDEOS,
            "completed_rhymes": completed_rhymes,
            "total_rhymes": total_rhymes,
            "quizzes_completed": quizzes_completed,
            "total_quizzes": total_quizzes,
            "total_stars": total_stars,
            "level": level,
            "avatar_emoji": user.avatar_emoji(),
            "activity_dates": [item["when"].isoformat() for item in activities],
        },
    )


# Existing code can continue using this function name.
@login_required(login_url="accounts:login")
def profile_redirect(request):
    return profile(request)


# ============================================================
# LEARNER SETTINGS
# ============================================================

SETTINGS_DEFAULTS = {
    "language": "en-us",
    "daily_goal": 30,
    "content_filter": "strict",
    "auto_play": True,
    "offline_mode": False,
    "theme": "light",
    "font_size": "medium",
    "master_volume": 80,
    "music_volume": 70,
    "effects_volume": 90,
    "notifications": True,
    "learning_reminders": True,
    "achievement_notifications": True,
    "screen_time_limit": "60",
    "quiz_permissions": "all",
    "purchase_settings": "password",
}

SETTINGS_LANGUAGES = [
    ("en-us", "English (US)"),
    ("te", "Telugu"),
    ("hi", "Hindi"),
    ("ta", "Tamil"),
    ("kn", "Kannada"),
    ("ml", "Malayalam"),
]

SETTINGS_DAILY_GOALS = [(15, "15 Minutes"), (30, "30 Minutes"), (45, "45 Minutes"), (60, "60 Minutes")]
SETTINGS_CONTENT_FILTERS = [("strict", "Strict"), ("moderate", "Moderate"), ("standard", "Standard")]
SETTINGS_THEMES = [("light", "Light"), ("dark", "Dark"), ("auto", "Auto")]
SETTINGS_FONT_SIZES = [("small", "Small"), ("medium", "Medium"), ("large", "Large")]
SETTINGS_SCREEN_TIME = [("30", "30 Minutes per day"), ("60", "1 Hour per day"), ("90", "1.5 Hours per day"), ("120", "2 Hours per day")]
SETTINGS_QUIZ_PERMISSIONS = [("all", "Allow all quizzes"), ("age", "Age-appropriate quizzes only"), ("none", "Ask a parent first")]
SETTINGS_PURCHASE = [("password", "Require password"), ("parent", "Parent approval required"), ("blocked", "Block purchases")]


def _settings_state(request):
    saved = request.session.get("learning_settings", {})
    state = {**SETTINGS_DEFAULTS, **saved}
    state["age_group"] = request.user.age_group or "4-6"
    return state


@never_cache
@login_required(login_url="accounts:login")
def games(request):
    """Child-friendly games hub. Games are browser-based and need no database setup."""
    return render(request, "core/games.html")


@never_cache
@login_required(login_url="accounts:login")
@require_http_methods(["GET", "POST"])
def settings_page(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except (TypeError, ValueError, UnicodeDecodeError):
            return JsonResponse({"ok": False, "error": "Invalid settings payload."}, status=400)

        state = _settings_state(request)
        changed = False

        if "language" in payload and payload["language"] in dict(SETTINGS_LANGUAGES):
            state["language"] = payload["language"]
            changed = True
        if "age_group" in payload and payload["age_group"] in dict(User.AGE_GROUP_CHOICES):
            request.user.age_group = payload["age_group"]
            request.user.save(update_fields=["age_group"])
            state["age_group"] = request.user.age_group
            changed = True
        if "daily_goal" in payload:
            try:
                value = int(payload["daily_goal"])
            except (TypeError, ValueError):
                value = None
            if value in dict(SETTINGS_DAILY_GOALS):
                state["daily_goal"] = value
                changed = True
        for key, allowed in {
            "content_filter": dict(SETTINGS_CONTENT_FILTERS),
            "theme": dict(SETTINGS_THEMES),
            "font_size": dict(SETTINGS_FONT_SIZES),
            "screen_time_limit": dict(SETTINGS_SCREEN_TIME),
            "quiz_permissions": dict(SETTINGS_QUIZ_PERMISSIONS),
            "purchase_settings": dict(SETTINGS_PURCHASE),
        }.items():
            if key in payload and payload[key] in allowed:
                state[key] = payload[key]
                changed = True

        for key in ("auto_play", "offline_mode", "notifications", "learning_reminders", "achievement_notifications"):
            if key in payload and isinstance(payload[key], bool):
                state[key] = payload[key]
                changed = True

        for key in ("master_volume", "music_volume", "effects_volume"):
            if key in payload:
                try:
                    value = max(0, min(100, int(payload[key])))
                except (TypeError, ValueError):
                    continue
                state[key] = value
                changed = True

        if changed:
            request.session["learning_settings"] = state
            request.session.modified = True

        return JsonResponse({"ok": True, "settings": state})

    return render(
        request,
        "core/settings.html",
        {
            "settings": _settings_state(request),
            "languages": SETTINGS_LANGUAGES,
            "age_groups": User.AGE_GROUP_CHOICES,
            "daily_goals": SETTINGS_DAILY_GOALS,
            "content_filters": SETTINGS_CONTENT_FILTERS,
            "themes": SETTINGS_THEMES,
            "font_sizes": SETTINGS_FONT_SIZES,
            "screen_time_options": SETTINGS_SCREEN_TIME,
            "quiz_permission_options": SETTINGS_QUIZ_PERMISSIONS,
            "purchase_options": SETTINGS_PURCHASE,
            "is_parent": request.user.is_parent,
        },
    )
