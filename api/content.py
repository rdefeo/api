from pylru import FunctionCacheManager
from tornado.escape import json_decode
from tornado.httpclient import HTTPClient
from api.settings import CONTENT_URL


class Content(object):
    def __init__(self, cache_maxsize):
        self.product_cache = FunctionCacheManager(self.get_from_service, cache_maxsize)

    def get_from_service(self, _id):
        url = "%s/product_detail/%s.json" % (CONTENT_URL, _id)
        http_client = HTTPClient()
        response = http_client.fetch(url)
        data = json_decode(response.body)
        return {
            "title": data["title"],
            "attributes": data["attributes"],
            "images": data["images"],
            "brand": data["brand"],
            "prices": data["prices"]
        }
