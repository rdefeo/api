import logging
from tornado import gen
import tornado
from tornado.httpclient import HTTPClient, HTTPRequest
from tornado.web import RequestHandler, asynchronous
from tornado.escape import json_encode
from api.settings import DETECT_URL, SUGGEST_URL, CONTEXT_URL, LOGGING_LEVEL
from api import __version__


class Cache(RequestHandler):
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def initialize(self, product_cache):
        self.product_cache = product_cache

    def on_finish(self):
        pass

    def delete(self, *args, **kwargs):
        self.product_cache.clear()
        client = HTTPClient()
        url_suggest_clear = "%s/cache" % SUGGEST_URL
        self.logger.debug("clear suggest_cache,url=%s", url_suggest_clear)
        suggest_request = HTTPRequest(url_suggest_clear, method="DELETE")
        client.fetch(suggest_request)

        url_detect_clear = "%s/refresh" % DETECT_URL
        self.logger.debug("clear detect_cache,url=%s", url_detect_clear)
        detect_request = HTTPRequest(url_detect_clear, method="GET")
        client.fetch(detect_request)

        self.logger.debug("clear cache completed")
        self.finish()
