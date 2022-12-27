from accounts.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from testing.testcases import TestCase

LOGIN_URL = '/api/accounts/login/'
SIGNUP_URL = '/api/accounts/signup/'
LOGOUT_URL = '/api/accounts/logout/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
USER_PROFILE_DETAIL_URL = '/api/profiles/{}/'


class AccountApiTest(TestCase):

    def setUp(self):
        self.user = self.create_user('test_user')
        self.user_client = APIClient()

    def test_login(self):
        # cannot use get
        response = self.user_client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password'
        })
        self.assertEqual(response.status_code, 405)

        # username not exist
        response = self.user_client.post(LOGIN_URL, {
            'username': 'username not exist',
            'password': 'correct password'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors']['username'][0], 'The username does not exist.')

        # password wrong
        response = self.user_client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'Username and password do not match.')

        # login status
        response = self.user_client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_logged_in'], False)

        # login successfully
        response = self.user_client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)

        # login status
        response = self.user_client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login successfully
        self.user_client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password'
        })
        # login status
        response = self.user_client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_logged_in'], True)
        
        # cannot use get
        response = self.user_client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # logout successfully
        response = self.user_client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)

        # login status
        response = self.user_client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        # cannot use get
        response = self.user_client.get(LOGIN_URL, {
            'username': 'test_username',
            'email': 'test@gmail.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 405)

        # username exist
        response = self.user_client.post(SIGNUP_URL, {
            'username': self.user.username,
            'email': 'test@gmail.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors']['username'][0], 'This username has been used.')

        # email exist
        response = self.user_client.post(SIGNUP_URL, {
            'username': 'newusername',
            'email': self.user.email,
            'password': 'password'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors']['email'][0], 'This email has been used.')

        # username too short
        response = self.user_client.post(SIGNUP_URL, {
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 400)

        # password too long
        response = self.user_client.post(SIGNUP_URL, {
            'username': 'newusername',
            'email': 'newusername',
            'password': 'correct passworddddddddddddddddddddddddddddddddd'
        })
        self.assertEqual(response.status_code, 400)

        # signup successfully
        response = self.user_client.post(SIGNUP_URL, {
            'username': 'newusername',
            'email': 'newusername@gmail.com',
            'password': 'correct password'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['success'], True)

        created_user_id = response.data['user']['id']
        profile = UserProfile.objects.get(user_id=created_user_id)
        self.assertEqual(isinstance(profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)

        # login status
        response = self.user_client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_logged_in'], True)


class UserProfileAPITests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('test_user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('test_user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_update(self):
        user1_profile = self.user1.profile
        user1_profile.nickname = 'old nickname'
        user1_profile.save()
        url = USER_PROFILE_DETAIL_URL.format(user1_profile.id)

        # user 2 cannot update
        response = self.user2_client.put(url, {
            'nickname': 'new nickname'
        })
        self.assertEqual(response.status_code, 403)
        user1_profile.refresh_from_db()
        self.assertEqual(user1_profile.nickname, 'old nickname')

        # user 1 can update
        response = self.user1_client.put(url, {
            'nickname': 'new nickname'
        })
        self.assertEqual(response.status_code, 200)
        user1_profile.refresh_from_db()
        self.assertEqual(user1_profile.nickname, 'new nickname')

        # update avatar
        response = self.user1_client.put(url, {
            'avatar': SimpleUploadedFile(
                name='my-avatar.jpeg',
                content=str.encode('fake image'),
                content_type='image/jpeg'
            )
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('my-avatar' in response.data['avatar'], True)
        user1_profile.refresh_from_db()
        self.assertIsNotNone(user1_profile.avatar)
        