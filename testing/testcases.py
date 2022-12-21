from comments.models import Comment
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as DjangoTestCase
from friendships.models import Friendship
from likes.models import Like
from newsfeeds.models import NewsFeed
from rest_framework.test import APIClient
from tweets.models import Tweet


class TestCase(DjangoTestCase):
    
    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_user'):
            return self._anonymous_user

        self._anonymous_user = APIClient()
        return self._anonymous_user
        
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

    def create_friendship(self, from_user, to_user):
        return Friendship.objects.create(from_user=from_user, to_user=to_user)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'any comment'
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)

    def create_like(self, user, target):
        like, _ = Like.objects.get_or_create(
            object_id=target.id,
            user=user,
            content_type=ContentType.objects.get_for_model(target.__class__)
        )

        return like
