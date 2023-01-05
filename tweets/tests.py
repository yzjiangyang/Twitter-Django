from datetime import timedelta
from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import Tweet, TweetPhoto
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

        # cache a list of tweets
        tweet2 = self.create_tweet(test_user)
        key = 'test_key'
        conn.lpush(key, DjangoModelSerializer.serialize(tweet))
        conn.lpush(key, DjangoModelSerializer.serialize(tweet2))
        serialized_list = conn.lrange(key, 0, -1)
        objects = []
        for serialized_data in serialized_list:
            deserialized_data = DjangoModelSerializer.deserialize(serialized_data)
            objects.append(deserialized_data)
        self.assertEqual(objects, [tweet2, tweet])
