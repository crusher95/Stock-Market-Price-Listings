import ast
import json
from itertools import islice

import redis as redis


class Redis:

    def __init__(self):
        self.__redis = redis.StrictRedis()

    def redis_set(self, value, key='data'):
        return self.__redis.set(key, value)

    def redis_get(self, key='data'):
        return self.__redis.get(key)

    def fetch_top_10_stocks(self):
        return islice([json.loads(self.redis_get(key)) for key in self.__redis.keys()],10)

    def search_for_key(self, search):
        return islice([json.loads(self.redis_get(key)) for key in self.__redis.keys(pattern=search.upper()+'*')],10)