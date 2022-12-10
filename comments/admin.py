from comments.models import Comment
from django.contrib import admin


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('user', 'tweet', 'content', 'created_at')
