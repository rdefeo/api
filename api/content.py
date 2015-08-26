from pylru import FunctionCacheManager
from tornado.escape import json_decode
from tornado.httpclient import HTTPClient
from tornado.log import app_log
from api.settings import CONTENT_URL
from datetime import datetime


class Content(object):
    def __init__(self, cache_maxsize):
        self.product_cache = FunctionCacheManager(self.get_from_service, cache_maxsize)

    def clear(self):
        self.product_cache.clear()

    def get_from_service(self, _id):
        try:
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
                "prices": data["prices"],
                "updated": data["updated"] if "updated" in data else datetime(2015, 1, 1).isoformat()
            }
        except:
            app_log.error("get_from_service,_id=%s", _id)
            return None
            # raise
