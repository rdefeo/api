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
        http_client.close()
        return {
            "title": data["title"],
            "attributes": [x for x in data["attributes"] if "key" not in x["_id"] or x["_id"]["key"] not in ["small sizes", "large sizes"]],
            "images": data["images"],
            "brand": data["brand"],
            "prices": data["prices"]
        }
