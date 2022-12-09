from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'


class FriendshipApiTests(TestCase):
    def setUp(self):
        self.anonymous_client = APIClient()

        self.user1 = self.create_user('test_user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.followings = [
            self.create_friendship(self.user1, self.create_user('following{}'.format(i)))
            for i in range(3)
        ]

        self.user2 = self.create_user('test_user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        self.followers = [
            self.create_friendship(self.create_user('follower{}'.format(i)), self.user2)
            for i in range(2)
        ]

    def test_follow(self):
        # anonymous cannot follow
        url = FOLLOW_URL.format(self.user2.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # cannot use get
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 405)

        # user not exist
        response = self.user1_client.post(FOLLOW_URL.format(0))
        self.assertEqual(response.status_code, 404)

        # cannot follow yourself
        response = self.user1_client.post(FOLLOW_URL.format(self.user1.id))
        self.assertEqual(response.status_code, 400)

        # follow successfully
        friendships_count_before = Friendship.objects.count()
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], self.user2.username)

        # follow again
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 400)
        friendships_count_after = Friendship.objects.count()
        self.assertEqual(friendships_count_after, friendships_count_before + 1)

    def test_unfollow(self):
        # anonymous cannot unfollow
        url = UNFOLLOW_URL.format(self.user2.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # cannot unfollow yourself
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 400)

        # create friendship
        self.create_friendship(self.user1, self.user2)
        
        # cannot use get
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 405)
        
        # user not exist
        response = self.user2_client.post(UNFOLLOW_URL.format(0))
        self.assertEqual(response.status_code, 404)
        
        # user1 unfollow user2
        friendships_count_before = Friendship.objects.count()
        response = self.user1_client.post(url)
        friendships_count_after = Friendship.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(friendships_count_after, friendships_count_before - 1)
        
    def test_followings(self):
        # cannot use post
        url = FOLLOWINGS_URL.format(self.user1.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        self.assertEqual(
            response.data['followings'][0]['user']['id'],
            self.followings[-1].to_user_id
        )
        self.assertEqual(
            response.data['followings'][-1]['user']['id'],
            self.followings[0].to_user_id
        )

    def test_followers(self):
        # cannot use post
        url = FOLLOWERS_URL.format(self.user2.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        self.assertEqual(
            response.data['followers'][0]['user']['id'],
            self.followers[-1].from_user_id
        )
        self.assertEqual(
            response.data['followers'][-1]['user']['id'],
            self.followers[0].from_user_id
        )
