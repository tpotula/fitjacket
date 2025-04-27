# challenges/admin.py
from django.contrib import admin
from .models import Challenge, Participation

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'point_value')
    list_filter = ('difficulty',)
    search_fields = ('title', 'description')
    ordering = ('-point_value',)

@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'joined_at', 'completed_at', 'points_awarded')
    list_filter = ('completed_at', 'challenge__difficulty')
    search_fields = ('user__username', 'challenge__title')
    readonly_fields = ('points_awarded',)