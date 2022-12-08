from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet

TWEET_LIST_URL = '/api/tweets/'
TWEET_CREATE_URL = '/api/tweets/'


class TweetApiTests(TestCase):
    def setUp(self):
        self.anonymous_client = APIClient()

        self.user1 = self.create_user('test_user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.tweets1 = [self.create_tweet(self.user1) for _ in range(3)]

        self.user2 = self.create_user('test_user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        self.tweets2 = [self.create_tweet(self.user2) for _ in range(2)]

    def test_list(self):
        # missing user_id
        response = self.anonymous_client.get(TWEET_LIST_URL)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors'], 'missing user_id')

        # user1 tweets
        response = self.anonymous_client.get(
            TWEET_LIST_URL,
            {'user_id': self.user1.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 3)
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets1[-1].id)
        self.assertEqual(response.data['tweets'][-1]['id'], self.tweets1[0].id)

        # user2 tweets
        response = self.anonymous_client.get(
            TWEET_LIST_URL,
            {'user_id': self.user2.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 2)
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[-1].id)
        self.assertEqual(response.data['tweets'][-1]['id'], self.tweets2[0].id)

    def create(self):
        # anonymous user cannot post a tweet
        response = self.anonymous_client.post(
            TWEET_CREATE_URL,
            {'content': 'content'}
        )
        self.assertEqual(response.status_code, 403)

        # no content
        response = self.user1_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, 400)

        # content too short
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': '0' * 5})
        self.assertEqual(response.status_code, 400)

        # content too long
        response = self.user1_client.post(
            TWEET_CREATE_URL,
            {'content': '0' * 141}
        )
        self.assertEqual(response.status_code, 400)

        # post successfully
        tweets_count_before = Tweet.objects.count()
        response = self.user1_client.post(
            TWEET_CREATE_URL,
            {'content': 'any content'}
        )
        tweets_count_after = Tweet.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweets_count_after, tweets_count_before + 1)
        self.assertEqual(
            response.data['tweets']['user']['username'],
            self.user1.username
        )
