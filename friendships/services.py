from django.contrib.auth.models import User
from friendships.models import Friendship


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
