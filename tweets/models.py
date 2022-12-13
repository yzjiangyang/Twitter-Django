from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
from utils.time_helpers import utc_now


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)

    @property
    def hour_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def likes_set(self):
        return Like.objects.filter(
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(Tweet)
        ).order_by('-created_at')

    def __str__(self):
        return '{} {}: {}'.format(self.created_at, self.user, self.content)