from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'tweet_id', 'content', 'created_at', 'updated_at')


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