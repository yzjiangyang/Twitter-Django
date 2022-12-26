from accounts.models import UserProfile
from rest_framework.test import APIClient
from testing.testcases import TestCase

LOGIN_URL = '/api/accounts/login/'
SIGNUP_URL = '/api/accounts/signup/'
LOGOUT_URL = '/api/accounts/logout/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


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