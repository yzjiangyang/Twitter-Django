from datetime import timedelta
from testing.testcases import TestCase
from tweets.models import Tweet
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def test_hour_to_now(self):
        test_user = self.create_user('test_user')
        tweet = Tweet.objects.create(user=test_user, content="test content")
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hour_to_now, 10)
