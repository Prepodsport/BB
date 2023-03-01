from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('image', 'user', 'facebook', 'facebook', 'twitter', 'instagram', 'birth_date',)
    list_display_links = ('image', 'user')
    list_filter = ('user',)