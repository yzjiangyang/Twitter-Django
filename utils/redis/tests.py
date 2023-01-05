from testing.testcases import TestCase
from utils.redis.redis_client import RedisClient


class RedisTest(TestCase):

    def setUp(self):
        self.clear_cache()

    def test_redis_client(self):
        conn = RedisClient.get_connection()
        key = 'test_key'
        conn.lpush(key, 1)
        conn.lpush(key, 2)
        cached_list = conn.lrange(key, 0, -1)
        self.assertEqual(cached_list, [b'2', b'1'])

        # clear redis cache
        RedisClient.clear()
        cached_list = conn.lrange(key, 0, -1)
        self.assertEqual(cached_list, [])
