from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from newsfeeds.tasks import fanout_newsfeeds_main_task
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


class NewsFeedAsyncTaskTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')

    def test_fanout_main_task(self):
        tweet = self.create_tweet(self.user1)
        self.create_friendship(self.user2, self.user1)
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id)
        self.assertEqual(msg, '1 newsfeeds will be fanned out, 1 batches are created')
        self.assertEqual(NewsFeed.objects.count(), 2)
        cached_list = NewsFeedService.get_cached_newsfeeds_from_redis(self.user1.id)
        self.assertEqual(len(cached_list), 1)

        # add 2 more followers
        for i in range(2):
            user = self.create_user('test_user{}'.format(i))
            self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1)
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id)
        self.assertEqual(msg, '3 newsfeeds will be fanned out, 1 batches are created')
        self.assertEqual(NewsFeed.objects.count(), 6)
        cached_list = NewsFeedService.get_cached_newsfeeds_from_redis(self.user1.id)
        self.assertEqual(len(cached_list), 2)

        # another new follower
        new_user = self.create_user('new_user')
        self.create_friendship(new_user, self.user1)
        new_tweet = self.create_tweet(self.user1)
        msg = fanout_newsfeeds_main_task(new_tweet.id, self.user1.id)
        self.assertEqual(msg, '4 newsfeeds will be fanned out, 2 batches are created')
        self.assertEqual(NewsFeed.objects.count(), 11)
        cached_list = NewsFeedService.get_cached_newsfeeds_from_redis(self.user1.id)
        self.assertEqual(len(cached_list), 3)

        # post another tweet, and test NewsFeedService.fanout_to_followers
        another_tweet = self.create_tweet(self.user1)
        NewsFeedService.fanout_to_followers(another_tweet)
        self.assertEqual(NewsFeed.objects.count(), 16)
        cached_list = NewsFeedService.get_cached_newsfeeds_from_redis(self.user1.id)
        self.assertEqual(len(cached_list), 4)
