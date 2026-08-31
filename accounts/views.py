from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect


# IMPORTANT:
# Project uses AUTH_USER_MODEL = "accounts.User"
# So we MUST use get_user_model(), not django.contrib.auth.models.User
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

    Valid username + password
        -> Home Dashboard

    Invalid credentials
        -> Stay on Login page
    """

    # Always show the Login page when the user clicks Login.
    # If an old session exists, clear it first so Login never jumps to Home.
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
            return render(request, "accounts/login.html")

        if not password:
            messages.error(
                request,
                "Please enter your password."
            )
            return render(request, "accounts/login.html")

        # Authenticate using the project's custom User model
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

    return render(request, "accounts/login.html")


def register_view(request):
    """
    Registration page.

    Registration DOES NOT automatically login the user.

    After successful registration:
        Register -> Login -> verify credentials -> Home
    """

    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        account_type = request.POST.get(
            "account_type",
            "learner"
        )

        avatar = request.POST.get(
            "avatar",
            "boy"
        )

        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not full_name:
            messages.error(
                request,
                "Please enter your full name."
            )
            return render(
                request,
                "accounts/register.html"
            )

        if not username:
            messages.error(
                request,
                "Please choose a username."
            )
            return render(
                request,
                "accounts/register.html"
            )

        if not password1:
            messages.error(
                request,
                "Please create a password."
            )
            return render(
                request,
                "accounts/register.html"
            )

        if password1 != password2:
            messages.error(
                request,
                "Passwords do not match."
            )
            return render(
                request,
                "accounts/register.html"
            )

        # -----------------------------
        # CHECK USERNAME
        # -----------------------------

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "This username already exists. Please choose another one."
            )

            return render(
                request,
                "accounts/register.html"
            )

        # -----------------------------
        # CHECK EMAIL
        # -----------------------------

        if email and User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "This email is already registered."
            )

            return render(
                request,
                "accounts/register.html"
            )

        # -----------------------------
        # CREATE CUSTOM USER
        # -----------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=full_name
        )

        # Store registration choices in session
        request.session["account_type"] = account_type
        request.session["avatar"] = avatar

        # IMPORTANT:
        # DO NOT login automatically here.
        #
        # User must go to Login page and
        # verify username + password first.

        messages.success(
            request,
            "Registration successful! Please login to continue. 🎉"
        )

        return redirect("accounts:login")

    return render(
        request,
        "accounts/register.html"
    )


@login_required(login_url="accounts:login")
def home(request):
    """
    Protected Smart Learning Dashboard.

    User MUST be authenticated.
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

    return redirect("core:landing")