from notifications.models import Notification
from rest_framework.test import APIClient
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'


class NotificationTestCase(TestCase):

    def setUp(self):
        self.user1 = self.create_user('test_user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('test_user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_send_tweet_likes_notification(self):
        tweet = self.create_tweet(self.user1)
        self.user1_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': tweet.id
        })
        self.assertEqual(Notification.objects.count(), 0)

        # different user like the tweet, there is a notification
        self.user2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': tweet.id
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_comment_likes_notification(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)
        self.user1_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id
        })
        self.assertEqual(Notification.objects.count(), 0)

        # different user like the comment, there is a notification
        self.user2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_new_comments_notification(self):
        tweet = self.create_tweet(self.user1)
        self.user1_client.post(COMMENT_URL, {
            'tweet_id': tweet.id,
            'content': 'content'
        })
        self.assertEqual(Notification.objects.count(), 0)

        # different user comment on the tweet, there is a notification
        self.user2_client.post(COMMENT_URL, {
            'tweet_id': tweet.id,
            'content': 'content'
        })
        self.assertEqual(Notification.objects.count(), 1)
