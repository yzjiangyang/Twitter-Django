from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete
from likes.models import Like
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from utils.memcached.listeners import invalidate_object_cache
from utils.memcached.memcached_helper import MemcachedHelper
from utils.time_helpers import utc_now


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)

    def __str__(self):
        return '{} {}: {}'.format(self.created_at, self.user, self.content)

    @property
    def hour_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(Tweet)
        ).order_by('-created_at')

    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)


class TweetPhoto(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(null=True)
    order = models.IntegerField(default=0)
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES
    )
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return '{} {}'.format(self.tweet, self.file)


post_save.connect(invalidate_object_cache, sender=Tweet)
pre_delete.connect(invalidate_object_cache, sender=Tweet)
