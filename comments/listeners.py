from django.db.models import F


def incr_comments_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    if not created:
        return

    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') + 1
    )


def decr_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet

    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F('comments_count') - 1
    )
