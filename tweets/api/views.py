from django.utils.decorators import method_decorator
from newsfeeds.services import NewsFeedService
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail
)
from tweets.models import Tweet
from tweets.services import TweetService
from utils.paginations.endless_paginations import EndlessPagination


class TweetViewSet(viewsets.GenericViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated()]

    @method_decorator(ratelimit(key='user_or_ip', rate='5/s', method='GET', block=True))
    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response(
                {'errors': 'missing user_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.query_params['user_id']
        tweets = TweetService.get_cached_tweets_from_redis(user_id)
        page = self.paginator.get_paginated_cached_list_in_redis(tweets, request)
        if not page:
            tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(tweets)
        serializer = TweetSerializer(
            page,
            context={'request': request},
            many=True
        )

        return self.get_paginated_response(serializer.data)

    @method_decorator(ratelimit(key='user_or_ip', rate='5/s', method='GET', block=True))
    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(
            tweet,
            context={'request': request}
        )

        return Response(serializer.data)

    @method_decorator(ratelimit(key='user', rate='1/s', method='POST', block=True))
    @method_decorator(ratelimit(key='user', rate='5/m', method='POST', block=True))
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
            {'tweets': TweetSerializer(tweet, context={'request': request}).data},
            status=status.HTTP_201_CREATED
        )
