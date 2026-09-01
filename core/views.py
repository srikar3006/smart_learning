from django.contrib.auth.decorators import login_required

from django.db.models import Count, Q

from django.shortcuts import redirect, render

from django.templatetags.static import static

from django.views.decorators.cache import never_cache

from accounts.decorators import parent_required, learner_required

from accounts.forms import ChildCreationForm

from .video_data import CATEGORIES, VIDEOS

from progress.services import get_progress_summary

from quizzes.models import QuizAttempt

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
# PROFILE REDIRECT
# ============================================================

@login_required(
    login_url="accounts:login"
)
def profile_redirect(request):

    if request.user.is_parent:

        return redirect(
            "parent:dashboard"
        )

    return redirect(
        "core:home"
    )