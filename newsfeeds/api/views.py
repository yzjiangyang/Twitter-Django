from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        newsfeeds = NewsFeed.objects.filter(user=request.user).order_by('-created_at')
        serializer = NewsFeedSerializer(
            newsfeeds,
            context={'request': request},
            many=True
        )

        return Response({'newsfeeds': serializer.data})
