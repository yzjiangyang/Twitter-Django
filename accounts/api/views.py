from accounts.api.serializers import (
    LoginSerializer,
    SignupSerializer,
    UserSerializer,
    UserProfileSerializerForUpdate
)
from accounts.models import UserProfile
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.permissions import IsObjectOwner


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)


class AccountViewSet(viewsets.GenericViewSet):
    serializer_class = SignupSerializer

    @action(methods=['GET'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='GET', block=True))
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data

        return Response(data)

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = django_authenticate(
            request,
            username=username,
            password=password,
        )
        if not user or user.is_anonymous:
            return Response({
                'success': False,
                'message': 'Username and password do not match.',
            }, status=status.HTTP_400_BAD_REQUEST)
        django_login(request, user)

        return Response({
            'success': True,
            'user': UserSerializer(user).data
        })

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': SignupSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin
):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializerForUpdate
    permission_classes = (IsAuthenticated, IsObjectOwner)
