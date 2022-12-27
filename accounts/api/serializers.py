from accounts.models import UserProfile
from django.contrib.auth.models import User
from rest_framework import serializers, exceptions


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerWithProfile(serializers.ModelSerializer):
    nickname = serializers.CharField(source='profile.nickname')
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'avatar_url')

    def get_avatar_url(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None


class UserSerializerForTweet(UserSerializerWithProfile):

    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerForFriendship(UserSerializerWithProfile):
    pass


class UserSerializerForComment(UserSerializerWithProfile):
    pass


class UserSerializerForLike(UserSerializerWithProfile):
    pass


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data['username']
        if not User.objects.filter(username=username.lower()).exists():
            raise exceptions.ValidationError({
                'username': 'The username does not exist.'
            })
        return data


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def validate(self, data):
        username = data['username']
        email = data['email']
        if User.objects.filter(username=username.lower()).exists():
            raise exceptions.ValidationError({
                'username': 'This username has been used.'
            })
        if User.objects.filter(email=email.lower()).exists():
            raise exceptions.ValidationError({
                'email': 'This email has been used.'
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']
        user = User.objects.create_user(username, email, password)
        # create user profile
        user.profile
        return user


class UserProfileSerializerForUpdate(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar')
