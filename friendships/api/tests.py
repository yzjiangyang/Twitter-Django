from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from utils.paginations import FriendshipPagination

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'


class FriendshipApiTests(TestCase):
    def setUp(self):
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

        self.user3 = self.create_user('test_user3')
        self.user3_client = APIClient()
        self.user3_client.force_authenticate(self.user3)

        self.user4 = self.create_user('test_user4')
        self.user4_client = APIClient()
        self.user4_client.force_authenticate(self.user4)

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
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(
            response.data['results'][0]['user']['id'],
            self.followings[-1].to_user_id
        )
        self.assertEqual(
            response.data['results'][-1]['user']['id'],
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
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(
            response.data['results'][0]['user']['id'],
            self.followers[-1].from_user_id
        )
        self.assertEqual(
            response.data['results'][-1]['user']['id'],
            self.followers[0].from_user_id
        )

    def test_followings_pagination(self):
        page_size = FriendshipPagination.page_size
        max_page_size = FriendshipPagination.max_page_size
        for i in range(page_size * 2):
            following = self.create_user('test_following{}'.format(i))
            self.create_friendship(self.user3, following)
            if following.id % 2 == 0:
                self.create_friendship(self.user4, following)
        url = FOLLOWINGS_URL.format(self.user3.id)
        self._test_friendship_pagination(url, max_page_size, page_size)

        # anonymous user not follow anyone
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # user 3 followed everyone
        response = self.user3_client.get(url)
        self.assertEqual(response.status_code, 200)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

        # user 4 followed some, not all
        response = self.user4_client.get(url)
        self.assertEqual(response.status_code, 200)
        for result in response.data['results']:
            has_followed = result['user']['id'] % 2 == 0
            self.assertEqual(result['has_followed'], has_followed)

    def test_followers_pagination(self):
        page_size = FriendshipPagination.page_size
        max_page_size = FriendshipPagination.max_page_size
        for i in range(page_size * 2):
            follower = self.create_user('test_follower{}'.format(i))
            self.create_friendship(follower, self.user3)
            if follower.id % 2 == 0:
                self.create_friendship(self.user4, follower)
        url = FOLLOWERS_URL.format(self.user3.id)
        self._test_friendship_pagination(url, max_page_size, page_size)

        # anonymous user not follow anyone
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # user 3 not follow everyone
        response = self.user3_client.get(url)
        self.assertEqual(response.status_code, 200)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # user 4 followed some, not all
        response = self.user4_client.get(url)
        self.assertEqual(response.status_code, 200)
        for result in response.data['results']:
            has_followed = result['user']['id'] % 2 == 0
            self.assertEqual(result['has_followed'], has_followed)

    def _test_friendship_pagination(self, url, max_page_size, page_size):
        # test page 1
        response = self.anonymous_client.get(url, {
            'page': 1,
            'size': page_size
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], page_size * 2)
        self.assertEqual(response.data['total_page'], 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        # test page 2
        response = self.anonymous_client.get(url, {
            'page': 2,
            'size': page_size
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], page_size * 2)
        self.assertEqual(response.data['total_page'], 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['has_next_page'], False)

        # test page 3
        response = self.anonymous_client.get(url, {
            'page': 3,
            'size': page_size
        })
        self.assertEqual(response.status_code, 404)

        # size > max_page_size
        response = self.anonymous_client.get(url, {
            'page': 1,
            'size': max_page_size + 1
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], page_size * 2)
        self.assertEqual(response.data['total_page'], 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        # size = 2
        response = self.anonymous_client.get(url, {
            'page': 1,
            'size': 2
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], page_size * 2)
        self.assertEqual(response.data['total_page'], page_size)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        response = self.anonymous_client.get(url, {
            'page': page_size,
            'size': 2
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], page_size * 2)
        self.assertEqual(response.data['total_page'], page_size)
        self.assertEqual(response.data['page_number'], page_size)
        self.assertEqual(response.data['has_next_page'], False)

