from django.contrib import admin
from newsfeeds.models import Newsfeed


@admin.register(Newsfeed)
class NewsfeedAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('user', 'tweet', 'created_at')