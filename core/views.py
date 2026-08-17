from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render

from accounts.decorators import parent_required
from accounts.forms import ChildCreationForm
from accounts.models import User
from progress.services import get_progress_summary
from quizzes.models import QuizAttempt
from rhymes.models import Category, Rhyme


def landing(request):
    # IMPORTANT:
    # Project open chesinappudu ALWAYS landing page first open avvali.
    # Login ayina user aina, logout user aina first landing page kanipistundi.
    return render(request, "core/landing.html")


@login_required
def home(request):
    if request.user.is_parent:
        return redirect("parent:dashboard")

    categories = list(
        Category.objects.prefetch_related("rhymes").all()[:6]
    )

    continue_learning = (
        Rhyme.objects.filter(
            is_published=True,
            progress_records__user=request.user,
            progress_records__completed=False,
        )
        .select_related("category")
        .distinct()[:4]
    )

    summary = get_progress_summary(request.user)

    featured = list(
        Rhyme.objects.filter(
            is_published=True
        ).select_related("category")[:4]
    )

    context = {
        "categories": categories,
        "continue_learning": continue_learning,
        "featured": featured,
        "summary": summary,
    }

    return render(request, "core/home.html", context)


@parent_required
def parent_dashboard(request):
    children = list(
        request.user.children.filter(is_active=True)
        .annotate(
            completed_rhymes=Count(
                "rhyme_progress",
                filter=Q(rhyme_progress__completed=True),
                distinct=True,
            ),
            quizzes_completed=Count(
                "quiz_attempts",
                filter=Q(quiz_attempts__completed_at__isnull=False),
                distinct=True,
            ),
        )
    )

    selected_child = None
    selected_child_id = request.GET.get("child")

    if selected_child_id:
        selected_child = next(
            (
                child
                for child in children
                if str(child.id) == str(selected_child_id)
            ),
            None,
        )

    if not selected_child and children:
        selected_child = children[0]

    child_summary = (
        get_progress_summary(selected_child)
        if selected_child
        else None
    )

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
        .order_by("-completed_at")[:8]
    )

    return render(
        request,
        "core/parent_dashboard.html",
        {
            "children": children,
            "selected_child": selected_child,
            "child_summary": child_summary,
            "recent_attempts": recent_attempts,
        },
    )


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

            return redirect("parent:dashboard")

    else:
        form = ChildCreationForm(parent=request.user)

    return render(
        request,
        "core/add_child.html",
        {"form": form},
    )


@login_required
def profile_redirect(request):
    return redirect(
        "parent:dashboard"
        if request.user.is_parent
        else "core:home"
    )