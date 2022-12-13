from likes.api.serializers import LikeSerializer, LikeSerializerForCreate
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class LikeViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

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
        like = serializer.save()
        return Response(
            LikeSerializer(like).data,
            status=status.HTTP_201_CREATED
        )
