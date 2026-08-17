from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def parent_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_parent:
            messages.error(request, "That area is available to parent accounts only.")
            return redirect("core:home")
        return view_func(request, *args, **kwargs)

    return wrapper


def learner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_learner:
            messages.error(request, "That area is part of the learner experience.")
            return redirect("parent:dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper
