from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .forms import LearnerRegistrationForm, ParentRegistrationForm


class KidLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_parent:
            return reverse("parent:dashboard")

        return reverse("core:home")


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        # Already logged-in users don't need registration.
        if request.user.is_authenticated:
            if request.user.is_parent:
                return redirect("parent:dashboard")

            return redirect("core:home")

        return render(
            request,
            self.template_name,
            {
                "learner_form": LearnerRegistrationForm(
                    prefix="learner"
                ),
                "parent_form": ParentRegistrationForm(
                    prefix="parent"
                ),
            },
        )

    def post(self, request):
        account_type = request.POST.get(
            "account_type",
            "learner",
        )

        if account_type == "parent":
            form = ParentRegistrationForm(
                request.POST,
                prefix="parent",
            )
        else:
            form = LearnerRegistrationForm(
                request.POST,
                prefix="learner",
            )

        if form.is_valid():
            # Create the account.
            # User is NOT automatically logged in.
            user = form.save()

            messages.success(
                request,
                "Registration successful! "
                "Please login to continue.",
            )

            # Registration → Login
            return redirect("accounts:login")

        return render(
            request,
            self.template_name,
            {
                "learner_form": LearnerRegistrationForm(
                    request.POST
                    if account_type == "learner"
                    else None,
                    prefix="learner",
                ),
                "parent_form": ParentRegistrationForm(
                    request.POST
                    if account_type == "parent"
                    else None,
                    prefix="parent",
                ),
                "selected_account_type": account_type,
            },
        )


def logout_view(request):
    logout(request)

    messages.info(
        request,
        "You have logged out safely. See you next time! 👋",
    )

    return redirect("core:landing")