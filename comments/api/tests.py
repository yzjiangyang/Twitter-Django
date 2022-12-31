from comments.models import Comment
from rest_framework.test import APIClient
from testing.testcases import TestCase

COMMENT_UTL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'
TWEET_DETAIL_URL = '/api/tweets/{}/'
TWEET_LIST_URL = '/api/tweets/'
NEWSFEED_LIST_URL = '/api/newsfeeds/'


class CommentApiTest(TestCase):
    
    def setUp(self):
        self.user1 = self.create_user('test_user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.tweet = self.create_tweet(self.user1)

        self.user2 = self.create_user('test_user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_list(self):
        # missing params
        response = self.anonymous_client.get(COMMENT_UTL)
        self.assertEqual(response.status_code, 400)

        # with tweet_id
        response = self.anonymous_client.get(COMMENT_UTL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # create 2 comments
        self.create_comment(self.user1, self.tweet)
        self.create_comment(self.user2, self.tweet)
        response = self.anonymous_client.get(COMMENT_UTL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['user']['username'], self.user2.username)
        self.assertEqual(response.data['comments'][1]['user']['username'],self.user1.username)
    
    def test_create(self):
        # anonymous user cannot comment
        response = self.anonymous_client.post(COMMENT_UTL)
        self.assertEqual(response.status_code, 403)

        # no parameter
        response = self.user2_client.post(COMMENT_UTL)
        self.assertEqual(response.status_code, 400)

        # missing one parameter
        response = self.user2_client.post(COMMENT_UTL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)
        response = self.user2_client.post(COMMENT_UTL,{'content': 'comment'})
        self.assertEqual(response.status_code, 400)
        
        # tweet id not valid
        response = self.user2_client.post(COMMENT_UTL, {
            'tweet_id': 0,
            'content': 'comment'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors']['message'][0], 'tweet does not exist.')

        # content too long
        response = self.user2_client.post(COMMENT_UTL, {
            'tweet_id': self.tweet.id,
            'content': '0' * 141
        })
        self.assertEqual(response.status_code, 400)

        # comment successfully
        response = self.user2_client.post(COMMENT_UTL, {
            'tweet_id': self.tweet.id,
            'content': 'comment'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content'], 'comment')
        self.assertEqual(response.data['user']['username'], self.user2.username)

    def test_update(self):
        comment = self.create_comment(self.user1, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)
        # anonymous cannot update
        response = self.anonymous_client.put(url, {'content': 'new content'})
        self.assertEqual(response.status_code, 403)

        # other user cannot update
        response = self.user2_client.put(url, {'content': 'new content'})
        self.assertEqual(response.status_code, 403)

        # can only update content
        updated_at_before = comment.updated_at
        another_tweet = self.create_tweet(self.user1)
        response = self.user1_client.put(url, {
            'user_id': self.user2.id,
            'tweet_id': another_tweet.id,
            'content': 'new content'
        })
        comment.refresh_from_db()
        updated_at_after = comment.updated_at
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.user_id, self.user1.id)
        self.assertEqual(comment.tweet_id, self.tweet.id)
        self.assertNotEqual(updated_at_after, updated_at_before)

    def test_destroy(self):
        comment = self.create_comment(self.user1, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # anonymous cannot delete
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # other user cannot delete
        response = self.user2_client.delete(url,)
        self.assertEqual(response.status_code, 403)

        # delete successfully
        comment_count_before = Comment.objects.count()
        response = self.user1_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        comment_count_after = Comment.objects.count()
        self.assertEqual(comment_count_before - 1, comment_count_after)

    def test_comments_count(self):
        # create comment. test tweet list api
        self.create_comment(self.user1, self.tweet)
        response = self.anonymous_client.get(TWEET_LIST_URL, {
            'user_id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['comments_count'], 1)

        # test tweet detail
        url = TWEET_DETAIL_URL.format(self.tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 1)

        # test newsfeed api
        self.create_newsfeed(self.user1, self.tweet)
        response = self.user1_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['comments_count'], 1)
