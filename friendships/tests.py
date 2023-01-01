from friendships.models import Friendship
from friendships.services import FriendshipService
from testing.testcases import TestCase


class FriendshipServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('test_user1')
        self.user2 = self.create_user('test_user2')
        self.user3 = self.create_user('test_user3')

    def test_get_following_user_id_set(self):
        user4 = self.create_user('test_user4')
        for to_user in [self.user1, self.user2, self.user3]:
            self.create_friendship(user4, to_user)

        user_id_set = FriendshipService.get_following_user_id_set(user4.id)
        self.assertEqual(
            user_id_set,
            set([self.user1.id, self.user2.id, self.user3.id]),
        )

        # get user_id_set again (get from cache)
        user_id_set = FriendshipService.get_following_user_id_set(user4.id)
        self.assertEqual(
            user_id_set,
            set([self.user1.id, self.user2.id, self.user3.id]),
        )

        # delete a user
        Friendship.objects.filter(from_user=user4, to_user=self.user1).delete()
        user_id_set = FriendshipService.get_following_user_id_set(user4.id)
        self.assertEqual(user_id_set, set([self.user2.id, self.user3.id]))

        # add a user
        user5 = self.create_user('test_user5')
        self.create_friendship(user4, user5)
        user_id_set = FriendshipService.get_following_user_id_set(user4.id)
        self.assertEqual(
            user_id_set,
            set([self.user2.id, self.user3.id, user5.id]),
        )
