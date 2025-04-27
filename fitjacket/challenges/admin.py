from django.contrib import admin
from .models import Challenge

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display  = ('title', 'start_date', 'end_date')
    search_fields = ('title',)
    list_filter   = ('start_date', 'end_date')
