from datetime import datetime, timedelta

from pylru import FunctionCacheManager, lrucache
from tornado.escape import json_decode
from tornado.httpclient import HTTPClient
from tornado.log import app_log

from api.settings import CONTENT_URL


class Content(object):
    def __init__(self, cache_maxsize):
        self.cache = lrucache(cache_maxsize)

    def clear(self):
        self.cache.clear()

    def get_product(self, _id, now: datetime=None):
        now = datetime.now() if now is None else now
        if _id in self.cache and self.cache[_id][1].isoformat() > (now - timedelta(hours=8)).isoformat():
            return self.cache[_id][0]
        else:
            data = self._get_from_service(_id)
            self.cache[_id] = (data, now)
            return data

    def _get_from_service(self, _id):
        try:
            url = "%s/product_detail/%s.json" % (CONTENT_URL, _id)
            http_client = HTTPClient()
            response = http_client.fetch(url)
            data = json_decode(response.body)
            http_client.close()
            return {
                "title": data["title"],
                "attributes": [x for x in data["attributes"] if
                               "key" not in x["_id"] or x["_id"]["key"] not in ["small sizes", "large sizes"]],
                "images": data["images"],
                "brand": data["brand"],
                "prices": data["prices"],
                "updated": data["updated"] if "updated" in data else datetime(2015, 1, 1).isoformat()
            }
        except:
            app_log.error("get_from_service,_id=%s", _id)
            return None
            # raise
