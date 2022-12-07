from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase


class TestCase(DjangoTestCase):

    def create_user(self, username, email=None, password=None):
        if email is None:
            email = '{}@gmail.com'.format(username)
        if password is None:
            password = 'correct password'

        return User.objects.create_user(username, email, password)
