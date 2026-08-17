from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class LearnerAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "account_type",
        "parent",
        "age_group",
        "is_staff",
        "created_at",
    )
    list_filter = ("account_type", "age_group", "avatar", "is_staff", "is_active")
    search_fields = ("username", "first_name", "email", "parent__username")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Smart Learning profile",
            {"fields": ("account_type", "avatar", "age_group", "parent_email", "parent", "is_child_learner")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Smart Learning profile",
            {"fields": ("account_type", "avatar", "age_group", "parent")},
        ),
    )
