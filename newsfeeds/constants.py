from django.conf import settings

FANOUT_BATCH_SIZE = 100 if not settings.TESTING else 3
