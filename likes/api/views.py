from django.utils.decorators import method_decorator
from inbox.services import NotificationService
from likes.api.serializers import (
    LikeSerializer,
    LikeSerializerForCreate,
    LikeSerializerForCancel
)
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class LikeViewSet(viewsets.GenericViewSet):
    serializer_class = LikeSerializerForCancel
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def create(self, request):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check your input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        like, created = serializer.save()
        if created:
            NotificationService.send_like_notification(like)
        return Response(
            LikeSerializer(like).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def cancel(self, request):
        serializer = LikeSerializerForCancel(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check your input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted = serializer.cancel()
        return Response({
            'success': True,
            'deleted': deleted
        }, status=status.HTTP_200_OK)
