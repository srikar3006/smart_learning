from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST


# IMPORTANT:
# Project uses AUTH_USER_MODEL = "accounts.User"
User = get_user_model()


def landing(request):
    """
    First page of the project.
    Logged-in users are sent to Home.
    Logged-out users see the landing page.
    """
    if request.user.is_authenticated:
        return redirect("core:home")

    return render(request, "core/landing.html")


def login_view(request):
    """
    Login page.
    """

    # If already logged in and Login is opened, clear old session.
    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username:
            messages.error(
                request,
                "Please enter your username."
            )
            return render(
                request,
                "accounts/login.html"
            )

        if not password:
            messages.error(
                request,
                "Please enter your password."
            )
            return render(
                request,
                "accounts/login.html"
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                "Login successful! Welcome back! 🎉"
            )

            return redirect("core:home")

        messages.error(
            request,
            "Invalid username or password. Please try again."
        )

    return render(
        request,
        "accounts/login.html"
    )


@login_required(login_url="accounts:login")
@require_POST
def change_password(request):
    """
    Change password for the currently authenticated user only.
    """

    form = PasswordChangeForm(
        request.user,
        request.POST
    )

    if form.is_valid():

        new_password = form.cleaned_data["new_password1"]

        # New password must be different from current password.
        if request.user.check_password(new_password):

            messages.error(
                request,
                "New password must be different from your current password."
            )

            return redirect(
                "/profile/?change_password=1"
            )

        # Django securely hashes the new password.
        form.save()

        # Keep current user logged in after changing password.
        update_session_auth_hash(
            request,
            request.user
        )

        messages.success(
            request,
            "Password changed successfully. Your new password is now active."
        )

        return redirect(
            "core:profile"
        )

    errors = []

    for field_errors in form.errors.values():
        errors.extend(field_errors)

    messages.error(
        request,
        errors[0]
        if errors
        else "Please correct the password fields and try again."
    )

    return redirect(
        "/profile/?change_password=1"
    )


def register_view(request):
    """
    Create an account using:
    - Full name
    - Username
    - Password
    - Confirm password
    - Avatar
    """

    selected_role = request.GET.get(
        "type",
        "learner"
    ).strip().lower()

    if selected_role not in {"learner", "parent"}:
        selected_role = "learner"

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password1 = request.POST.get(
            "password1",
            ""
        )

        password2 = request.POST.get(
            "password2",
            ""
        )

        account_type = request.POST.get(
            "account_type",
            selected_role
        ).strip().lower()

        avatar = request.POST.get(
            "avatar",
            "boy"
        ).strip().lower()

        if account_type not in {"learner", "parent"}:
            account_type = "learner"

        context = {
            "selected_role": account_type
        }

        if not full_name:

            messages.error(
                request,
                "Please enter your full name."
            )

            return render(
                request,
                "accounts/register.html",
                context
            )

        if not username:

            messages.error(
                request,
                "Please choose a username."
            )

            return render(
                request,
                "accounts/register.html",
                context
            )

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "This username already exists. Please choose another one."
            )

            return render(
                request,
                "accounts/register.html",
                context
            )

        if not password1:

            messages.error(
                request,
                "Please create a password."
            )

            return render(
                request,
                "accounts/register.html",
                context
            )

        if password1 != password2:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "accounts/register.html",
                context
            )

        try:

            validate_password(
                password1,
                user=User(
                    username=username,
                    first_name=full_name,
                ),
            )

        except ValidationError as exc:

            for error in exc.messages:
                messages.error(
                    request,
                    error
                )

            return render(
                request,
                "accounts/register.html",
                context
            )

        allowed_avatars = {
            choice[0]
            for choice in User.AVATAR_CHOICES
        }

        if avatar not in allowed_avatars:
            avatar = "boy"

        User.objects.create_user(
            username=username,
            password=password1,
            first_name=full_name,
            account_type=account_type,
            avatar=(
                avatar
                if account_type == "learner"
                else "star"
            ),
            is_child_learner=(
                account_type == "learner"
            ),
        )

        messages.success(
            request,
            "Registration successful! Please login to continue. 🎉"
        )

        return redirect(
            "accounts:login"
        )

    return render(
        request,
        "accounts/register.html",
        {
            "selected_role": selected_role
        }
    )


@login_required(login_url="accounts:login")
def home(request):
    """
    Protected Smart Learning Dashboard.
    """

    return render(
        request,
        "home.html"
    )


def logout_view(request):
    """
    Logout user and return to landing page.
    """

    logout(request)

    messages.info(
        request,
        "You have logged out safely. See you next time! 👋"
    )

    return redirect(
        "core:landing"
    )