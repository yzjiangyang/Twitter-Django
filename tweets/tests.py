from datetime import timedelta
from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import Tweet, TweetPhoto
from tweets.services import TweetService
from twitter.cache import USER_TWEETS_PATTERN
from utils.redis.redis_client import RedisClient
from utils.redis.redis_serializers import DjangoModelSerializer
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def test_hour_to_now(self):
        self.clear_cache()
        test_user = self.create_user('test_user')
        tweet = Tweet.objects.create(user=test_user, content="test content")
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hour_to_now, 10)

    def test_upload_tweet_photo(self):
        self.clear_cache()
        user = self.create_user('test_user')
        tweet = self.create_tweet(user)
        tweet_photo = TweetPhoto.objects.create(user=user, tweet=tweet)
        self.assertEqual(tweet_photo.user, user)
        self.assertEqual(TweetPhoto.objects.count(), 1)
        self.assertEqual(tweet_photo.status, TweetPhotoStatus.PENDING)

    def test_cache_tweet_to_redis(self):
        self.clear_cache()
        test_user = self.create_user('test_user')
        tweet = self.create_tweet(test_user)

        conn = RedisClient.get_connection()
        key = 'tweet:{}'.format(tweet.id)
        serialized_data = DjangoModelSerializer.serialize(tweet)
        conn.set(key, serialized_data)

        # key not exist
        data = conn.get('wrong_key')
        self.assertEqual(data, None)

        # right key
        data = conn.get(key)
        deserialized_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(tweet, deserialized_tweet)

        # clear redis cache
        RedisClient.clear()
        data = conn.get(key)
        self.assertEqual(data, None)

    def test_cached_tweet_list_in_redis(self):
        user = self.create_user('test_user')
        tweet_ids = []
        for _ in range(3):
            tweet = self.create_tweet(user)
            tweet_ids.append(tweet.id)
        tweet_ids = tweet_ids[::-1]

        key = USER_TWEETS_PATTERN.format(user_id=user.id)
        conn = RedisClient.get_connection()
        RedisClient.clear()
        # cache miss
        self.assertEqual(conn.exists(key), False)
        tweets = TweetService.get_cached_tweets_from_redis(user.id)
        self.assertEqual(tweet_ids, [tweet.id for tweet in tweets])
        # cache hit
        self.assertEqual(conn.exists(key), True)
        tweets = TweetService.get_cached_tweets_from_redis(user.id)
        self.assertEqual(tweet_ids, [tweet.id for tweet in tweets])

        # cache updated after a new tweet is created
        new_tweet = self.create_tweet(user)
        self.assertEqual(conn.exists(key), True)
        tweets = TweetService.get_cached_tweets_from_redis(user.id)
        tweet_ids.insert(0, new_tweet.id)
        self.assertEqual(tweet_ids, [tweet.id for tweet in tweets])
