from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService:

    @classmethod
    def fanout_to_followers(cls, tweet):
        followers = FriendshipService.get_followers(tweet.user)
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet) for follower in followers
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
