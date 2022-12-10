from django.contrib.auth.models import User
from django.db import models
from tweets.models import Tweet


class Newsfeed(models.Model):
    # who can see this tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'tweet'),)

    def __str__(self):
        return '{} inbox of {}: {}'.format(self.created_at, self.user, self.tweet)
