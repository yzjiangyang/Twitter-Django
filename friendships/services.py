from django.contrib.auth.models import User
from friendships.models import Friendship


class FriendshipService:

    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(to_user=user)
        followers_id = [friendship.from_user_id for friendship in friendships]
        followers = User.objects.filter(id__in=followers_id)

        return followers
    