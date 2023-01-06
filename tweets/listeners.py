def push_tweet_to_redis(sender, instance, created, **kwargs):
    from tweets.services import TweetService
    if not created:
        return

    TweetService.push_tweet_to_redis(instance)
