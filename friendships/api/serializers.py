from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


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
