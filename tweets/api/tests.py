from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.constants import TWEET_PHOTO_UPLOAD_LIMIT
from tweets.models import Tweet, TweetPhoto
from utils.endless_paginations import EndlessPagination

TWEET_LIST_URL = '/api/tweets/'
TWEET_CREATE_URL = '/api/tweets/'
TWEET_RETRIEVE_URL = '/api/tweets/{}/'


class TweetApiTests(TestCase):
    def setUp(self):
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
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['results'][0]['id'], self.tweets1[-1].id)
        self.assertEqual(response.data['results'][-1]['id'], self.tweets1[0].id)

        # user2 tweets
        response = self.anonymous_client.get(
            TWEET_LIST_URL,
            {'user_id': self.user2.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['id'], self.tweets2[-1].id)
        self.assertEqual(response.data['results'][-1]['id'], self.tweets2[0].id)

    def test_create(self):
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

    def test_retrieve(self):
        # invalid tweet id
        url = TWEET_RETRIEVE_URL.format(0)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # no comments
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_URL.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # add comments
        self.create_comment(self.user1, tweet)
        self.create_comment(self.user2, tweet)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(
            response.data['comments'][0]['user']['id'],
            self.user1.id
        )
        self.assertEqual(
            response.data['comments'][1]['user']['id'],
            self.user2.id
        )

    def test_create_tweet_with_pictures(self):
        # no files
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'content'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # empty files
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'content',
            'files': []
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # upload 1 picture
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'content',
            'files': SimpleUploadedFile(
                name='test.jpg',
                content=str.encode('a test image'),
                content_type='image/jpeg'
            )
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual('test' in response.data['tweets']['photo_urls'][0], True)

        # upload 2 pictures
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'content',
            'files': [SimpleUploadedFile(
                name='test{}.jpg'.format(i),
                content=str.encode('a test{} image'.format(i)),
                content_type='image/jpeg'
            ) for i in range(2)]
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 3)
        self.assertEqual('test0' in response.data['tweets']['photo_urls'][0], True)
        self.assertEqual('test1' in response.data['tweets']['photo_urls'][1], True)

        # test tweet retrieve url
        url = TWEET_RETRIEVE_URL.format(response.data['tweets']['id'])
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('test0' in response.data['photo_urls'][0], True)
        self.assertEqual('test1' in response.data['photo_urls'][1], True)

        # upload more than the limit
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'content',
            'files': [SimpleUploadedFile(
                name='test{}.jpg'.format(i),
                content=str.encode('a test{} image'.format(i)),
                content_type='image/jpeg'
            ) for i in range(TWEET_PHOTO_UPLOAD_LIMIT + 1)]
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['errors']['message'][0],
            f'You can only upload {TWEET_PHOTO_UPLOAD_LIMIT} photos at most'
        )

    def test_endless_pagination(self):
        page_size = EndlessPagination.page_size
        for i in range(2 * page_size - len(self.tweets1)):
            self.tweets1.append(self.create_tweet(self.user1))

        tweets = self.tweets1[::-1]

        # 1st page
        response = self.user1_client.get(TWEET_LIST_URL, {
            'user_id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], tweets[0].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], tweets[page_size - 1].id)

        # 2nd page
        response = self.user1_client.get(TWEET_LIST_URL, {
            'user_id': self.user1.id,
            'created_at__lt': tweets[page_size - 1].created_at
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], tweets[page_size].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], tweets[-1].id)

        # pull the latest page
        response = self.user1_client.get(TWEET_LIST_URL, {
            'user_id': self.user1.id,
            'created_at__gt': tweets[0].created_at
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)
        # user 1 create a new tweet
        new_tweet = self.create_tweet(self.user1)
        response = self.user1_client.get(TWEET_LIST_URL, {
            'user_id': self.user1.id,
            'created_at__gt': tweets[0].created_at
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_tweet.id)
