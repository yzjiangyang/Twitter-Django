from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import caches
from friendships.models import Friendship
from twitter.cache import FOLLOWING_PATTERNS

cache = caches['testing'] if settings.TESTING else caches['default']


class FriendshipService:

    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(to_user=user)
        followers_id = [friendship.from_user_id for friendship in friendships]
        followers = User.objects.filter(id__in=followers_id)

        return followers

    @classmethod
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user
        ).exists()

    @classmethod
    def get_following_user_id_set(cls, user_id):
        key = FOLLOWING_PATTERNS.format(user_id=user_id)
        following_user_id_set = cache.get(key)
        if following_user_id_set:
            return following_user_id_set

        friendships = Friendship.objects.filter(from_user_id=user_id)
        following_user_id_set = set([
            friendship.to_user_id for friendship in friendships
        ])
        cache.set(key, following_user_id_set)

        return following_user_id_set

    @classmethod
    def invalidate_following_cache(cls, user_id):
        key = FOLLOWING_PATTERNS.format(user_id=user_id)
        cache.delete(key)
