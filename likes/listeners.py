from django.db.models import F


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
