from django.db.models import F
from utils.redis.redis_helper import RedisHelper


def incr_likes_count(sender, instance, created, **kwargs):
    from comments.models import Comment
    from tweets.models import Tweet

    if not created:
        return

    if instance.content_object.__class__.__name__ != 'Tweet':
        Comment.objects.filter(id=instance.object_id).update(
            likes_count=F('likes_count') + 1
        )
    else:
        Tweet.objects.filter(id=instance.object_id).update(
            likes_count=F('likes_count') + 1
        )
    RedisHelper.incr_count(instance.content_object, 'likes_count')


def decr_likes_count(sender, instance, **kwargs):
    from comments.models import Comment
    from tweets.models import Tweet

    if instance.content_object.__class__.__name__ != 'Tweet':
        Comment.objects.filter(id=instance.object_id).update(
            likes_count=F('likes_count') - 1
        )
    else:
        Tweet.objects.filter(id=instance.object_id).update(
            likes_count=F('likes_count') - 1
        )
    RedisHelper.decr_count(instance.content_object, 'likes_count')
