from newsfeeds.services import NewsFeedService
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerWithComment
)
from tweets.models import Tweet


class TweetViewSet(viewsets.GenericViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response(
                {'errors': 'missing user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        return Response({'tweets': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer = TweetSerializerWithComment(tweet)
        return Response(serializer.data)

    def create(self, request):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(
            {'tweets': TweetSerializer(tweet).data},
            status=status.HTTP_201_CREATED
        )
