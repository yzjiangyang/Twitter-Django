from rest_framework.test import APIClient
from testing.testcases import TestCase

LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'
COMMENT_LIST_URL = '/api/comments/'
TWEET_DETAIL_URL = '/api/tweets/{}/'
TWEET_LIST_URL = '/api/tweets/'
NEWSFEED_LIST_URL = '/api/newsfeeds/'


class LikeApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('test_user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('test_user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_tweet_like(self):
        tweet = self.create_tweet(self.user1)

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.user1_client.get(LIKE_BASE_URL)
        self.assertEqual(response.status_code, 405)

        # wrong content type
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'wrong_type',
            'object_id': tweet.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertTrue('errors' in response.data)

        # wrong object id
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': 0
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['errors']['object_id'][0],
            'Object does not exist'
        )

        # post successfully
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': tweet.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], self.user1.username)

        # like again
        self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': tweet.id
        })
        self.assertEqual(tweet.like_set.count(), 1)

        # different user like the tweet
        self.user2_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': tweet.id
        })
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_like(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user2, tweet)

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.user1_client.get(LIKE_BASE_URL)
        self.assertEqual(response.status_code, 405)

        # wrong content type
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'wrong_type',
            'object_id': comment.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertTrue('errors' in response.data)

        # wrong object id
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': 0
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['errors']['object_id'][0],
            'Object does not exist'
        )

        # post successfully
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': comment.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], self.user1.username)

        # like again
        self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': comment.id
        })
        self.assertEqual(comment.like_set.count(), 1)

        # different user like the tweet
        self.user2_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': comment.id
        })
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel_likes(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)
        self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': tweet.id
        })
        self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': comment.id
        })
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # anonymous user cannot cancel like
        response = self.anonymous_client.post(LIKE_CANCEL_URL)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.user1_client.get(LIKE_CANCEL_URL)
        self.assertEqual(response.status_code, 405)

        # wrong content type
        response = self.user1_client.post(LIKE_CANCEL_URL, {
            'content_type': 'wrong_type',
            'object_id': tweet.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('errors' in response.data, True)

        # wrong object id
        response = self.user1_client.post(LIKE_CANCEL_URL, {
            'content_type': 'tweet',
            'object_id': -1
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('errors' in response.data, True)

        # user2 tries to cancel like
        response = self.user2_client.post(LIKE_CANCEL_URL, {
            'content_type': 'tweet',
            'object_id': tweet.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(tweet.like_set.count(), 1)

        # user1 can cancel
        response = self.user1_client.post(LIKE_CANCEL_URL, {
            'content_type': 'tweet',
            'object_id': tweet.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(tweet.like_set.count(), 0)

        response = self.user1_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': comment.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(comment.like_set.count(), 0)

    def test_likes_in_comment(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)

        # user1 liked
        self.user1_client.post(LIKE_BASE_URL, {
            'object_id': comment.id,
            'content_type': 'comment'
        })
        response = self.user1_client.get(COMMENT_LIST_URL, {
            'tweet_id': tweet.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # user2 checks
        response = self.user2_client.get(COMMENT_LIST_URL, {
            'tweet_id': tweet.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # user1 checks tweet detail url
        url = TWEET_DETAIL_URL.format(tweet.id)
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # user2 checks tweet detail url
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

    def test_likes_in_tweet(self):
        tweet = self.create_tweet(self.user1)
        # user1 liked
        self.user1_client.post(LIKE_BASE_URL, {
            'object_id': tweet.id,
            'content_type': 'tweet'
        })
        response = self.user1_client.get(TWEET_LIST_URL, {
            'user_id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['has_liked'], True)
        self.assertEqual(response.data['results'][0]['likes_count'], 1)

        # user2 checks
        response = self.user2_client.get(TWEET_LIST_URL, {
            'user_id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['has_liked'], False)
        self.assertEqual(response.data['results'][0]['likes_count'], 1)

        # test newsfeeds
        self.create_newsfeed(self.user1, tweet)
        response = self.user1_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['results'][0]['tweet']['has_liked'],
            True
        )
        self.assertEqual(
            response.data['results'][0]['tweet']['likes_count'],
            1
        )

        # user1 cancel the like
        self.user1_client.post(LIKE_CANCEL_URL, {
            'object_id': tweet.id,
            'content_type': 'tweet'
        })
        # check tweet list url
        response = self.user1_client.get(TWEET_LIST_URL, {
            'user_id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['has_liked'], False)
        self.assertEqual(response.data['results'][0]['likes_count'], 0)

        # check newsfeed url
        response = self.user1_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['results'][0]['tweet']['has_liked'],
            False
        )
        self.assertEqual(
            response.data['results'][0]['tweet']['likes_count'],
            0
        )
