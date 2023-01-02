from accounts.models import UserProfile
from django.conf import settings
from django.core.cache import caches
from twitter.cache import USER_PROFILE_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']


class UserService:

    @classmethod
    def get_profile_through_memcached(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        user_profile = cache.get(key)
        if user_profile:
            return user_profile

        user_profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
        cache.set(key, user_profile)
        return user_profile

    @classmethod
    def invalidate_profile_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        cache.delete(key)
