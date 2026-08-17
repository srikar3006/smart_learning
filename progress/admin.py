from django.contrib import admin
from .models import RhymeProgress, Badge, UserBadge


@admin.register(RhymeProgress)
class RhymeProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'rhyme', 'times_played', 'repeat_count', 'completed', 'last_played')
    list_filter = ('completed',)
    search_fields = ('user__username', 'rhyme__title')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_emoji', 'criteria_type', 'criteria_value')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
