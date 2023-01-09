from celery import shared_task
from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(limit=ONE_HOUR)
def fanout_newsfeeds_tasks(tweet_id):
    from newsfeeds.services import NewsFeedService

    tweet = Tweet.objects.get(id=tweet_id)
    followers = FriendshipService.get_followers(tweet.user)
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet) for follower in followers
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)
    # bulk_create won't trigger listener
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeeds_to_redis(newsfeed)
