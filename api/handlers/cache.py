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
        suggest_request = HTTPRequest("%s/cache" % SUGGEST_URL, method="DELETE")
        client.fetch(suggest_request)
        detect_request = HTTPRequest("%s/refresh" % DETECT_URL, method="GET")
        client.fetch(detect_request)

        self.finish()
