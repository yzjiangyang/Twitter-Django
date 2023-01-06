from newsfeeds.services import NewsFeedService
from testing.testcases import TestCase
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis.redis_client import RedisClient


class NewsFeedServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('test_user1')
        self.user2 = self.create_user('test_user2')

    def test_cache_newsfeeds_list_in_redis(self):
        newsfeed_ids = []
        for _ in range(3):
            tweet = self.create_tweet(self.user1)
            newsfeed = self.create_newsfeed(self.user2, tweet)
            newsfeed_ids.append(newsfeed.id)
        newsfeed_ids = newsfeed_ids[::-1]

        conn = RedisClient.get_connection()
        RedisClient.clear()
        # cache miss
        key = USER_NEWSFEEDS_PATTERN.format(user_id=self.user2.id)
        self.assertEqual(conn.exists(key), False)
        newsfeeds = NewsFeedService.get_cached_newsfeeds_from_redis(self.user2.id)
        self.assertEqual(newsfeed_ids, [newsfeed.id for newsfeed in newsfeeds])
        # cache hit
        self.assertEqual(conn.exists(key), True)
        newsfeeds = NewsFeedService.get_cached_newsfeeds_from_redis(self.user2.id)
        self.assertEqual(newsfeed_ids, [newsfeed.id for newsfeed in newsfeeds])

        # add a new newsfeed
        new_tweet = self.create_tweet(self.user1)
        new_newsfeed = self.create_newsfeed(self.user2, new_tweet)
        newsfeed_ids.insert(0, new_newsfeed.id)
        newsfeeds = NewsFeedService.get_cached_newsfeeds_from_redis(self.user2.id)
        self.assertEqual([newsfeed.id for newsfeed in newsfeeds], newsfeed_ids)
