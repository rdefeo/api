from tornado import gen
import tornado
from tornado.httpclient import HTTPClient, HTTPRequest
from tornado.web import RequestHandler, asynchronous
from tornado.escape import json_encode
from api.settings import DETECT_URL, SUGGEST_URL, CONTEXT_URL
from api import __version__


class Cache(RequestHandler):
    def initialize(self, product_cache):
        self.product_cache = product_cache

    def on_finish(self):
        pass

    def delete(self, *args, **kwargs):
        self.product_cache.clear()
        client = HTTPClient()
        request = HTTPRequest("%s/cache" % SUGGEST_URL, method="DELETE")
        client.fetch(request)