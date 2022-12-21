from inbox.services import NotificationService
from notifications.models import Notification
from rest_framework.test import APIClient
from testing.testcases import TestCase


class NotificationServiceTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('test_user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('test_user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_send_tweet_likes_notification(self):
        tweet = self.create_tweet(self.user1)
        like = self.create_like(self.user1, tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)

        # different user like the tweet, there's notification
        like = self.create_like(self.user2, tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_comment_likes_notification(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)
        like = self.create_like(self.user1, comment)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)

        # different user like the comment, there's notification
        like = self.create_like(self.user2, comment)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_new_comments_notification(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 0)

        # different user comment on th tweet, there's notification
        comment = self.create_comment(self.user2, tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 1)
