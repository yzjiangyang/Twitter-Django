from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FollowingUserIdSetMixin:

    @property
    def following_user_id_set(self):
        if self.context['request'].user.is_anonymous:
            return set()
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set

        following_user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id
        )
        setattr(self, '_cached_following_user_id_set', following_user_id_set)
        return following_user_id_set


class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        return obj.to_user_id in self.following_user_id_set


class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        return obj.from_user_id in self.following_user_id_set


class FollowingSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id', 'created_at')

    def validate(self, data):
        if data['from_user_id'] == data['to_user_id']:
            raise ValidationError({
                'message': 'You cannot follow yourself.'
            })
        if Friendship.objects.filter(
                from_user_id=data['from_user_id'],
                to_user_id=data['to_user_id']
        ).exists():
            raise ValidationError({
                'message': 'You have already followed this user.'
            })

        return data

    def create(self, validated_data):
        friendship = Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id']
        )

        return friendship
