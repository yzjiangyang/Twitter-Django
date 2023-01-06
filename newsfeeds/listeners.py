def push_newsfeed_to_redis(sender, instance, created, **kwargs):
    from newsfeeds.services import NewsFeedService
    if not created:
        return

    NewsFeedService.push_newsfeeds_to_redis(instance)
