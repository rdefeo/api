from datetime import datetime, timedelta

from pylru import FunctionCacheManager, lrucache
from tornado.escape import json_decode
from tornado.httpclient import HTTPClient
from tornado.log import app_log

from api.settings import CONTENT_URL


class Base:
    def __init__(self, cache_maxsize):
        self.cache = lrucache(cache_maxsize)
        self.initialize()

    def initialize(self):
        pass

    def clear(self):
        self.cache.clear()

    def get(self, key, now: datetime=None):
        now = datetime.now() if now is None else now
        if key in self.cache and self.cache[key][1].isoformat() > (now - timedelta(hours=8)).isoformat():
            return self.cache[key][0]
        else:
            data = self._get_from_service(key)
            self.cache[key] = (data, now)
            return data

    def _get_from_service(self, key):
        raise NotImplemented()
