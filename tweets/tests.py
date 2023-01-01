from datetime import timedelta
from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import Tweet, TweetPhoto
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
