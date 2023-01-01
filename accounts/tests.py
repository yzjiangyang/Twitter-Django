from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def test_user_profile(self):
        self.clear_cache()
        user = self.create_user('test_user')
        self.assertEqual(UserProfile.objects.count(), 0)
        profile = user.profile
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(isinstance(profile, UserProfile), True)
