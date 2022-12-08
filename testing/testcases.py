from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from tweets.models import Tweet


class TestCase(DjangoTestCase):

    def create_user(self, username, email=None, password=None):
        if email is None:
            email = '{}@gmail.com'.format(username)
        if password is None:
            password = 'correct password'

        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = "any content"

        return Tweet.objects.create(user=user, content=content)
