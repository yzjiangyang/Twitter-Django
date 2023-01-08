from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from likes.services import LikeService
from random import randint
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet
from utils.redis.redis_helper import RedisHelper


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment(source='cached_user')
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'tweet_id',
            'content',
            'created_at',
            'updated_at',
            'has_liked',
            'likes_count',
        )

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

    def get_likes_count(self, obj):
        if randint(0, 999) == 0:
            obj.refresh_from_db()
            actual_likes_count = obj.like_set.count()
            if obj.likes_count != actual_likes_count:
                obj.likes_count = actual_likes_count
                obj.save()
                return actual_likes_count

        return RedisHelper.get_count(obj, 'likes_count')


class CommentSerializerForCreate(serializers.ModelSerializer):
    tweet_id = serializers.IntegerField()
    
    class Meta:
        model = Comment
        fields = ('tweet_id', 'content')

    def validate(self, data):
        if not Tweet.objects.filter(id=data['tweet_id']).exists():
            raise ValidationError({
                'message': 'tweet does not exist.'
            })

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        tweet_id = validated_data['tweet_id']
        content = validated_data['content']

        return Comment.objects.create(
            user=user,
            tweet_id=tweet_id,
            content=content
        )


class CommentSerializerForUpdate(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('content',)

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()

        return instance
