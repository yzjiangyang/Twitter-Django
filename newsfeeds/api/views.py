from django.utils.decorators import method_decorator
from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from ratelimit.decorators import ratelimit
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from utils.paginations.endless_paginations import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination
    queryset = NewsFeed.objects.all()

    @method_decorator(ratelimit(key='user', rate='5/s', method='GET', block=True))
    def list(self, request):
        newsfeeds = NewsFeedService.get_cached_newsfeeds_from_redis(request.user.id)
        page = self.paginator.get_paginated_cached_list_in_redis(newsfeeds, request)
        if not page:
            newsfeeds = NewsFeed.objects.filter(user_id=request.user.id).order_by('-created_at')
            page = self.paginate_queryset(newsfeeds)
        serializer = NewsFeedSerializer(
            page,
            context={'request': request},
            many=True
        )

        return self.get_paginated_response(serializer.data)
