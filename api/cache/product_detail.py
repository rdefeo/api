from datetime import datetime, timedelta

from pylru import FunctionCacheManager, lrucache
from tornado.escape import json_decode
from tornado.httpclient import HTTPClient
from tornado.log import app_log
from api.cache.base import Base

from api.settings import CONTENT_URL


class ProductDetail(Base):
    def _get_from_service(self, _id):
        try:
            url = "%s/product_detail/%s.json" % (CONTENT_URL, _id)
            http_client = HTTPClient()
            response = http_client.fetch(url)
            data = json_decode(response.body)
            http_client.close()
            return {
                "_id": data["_id"],
                "sequence": data["sequence"] if "sequence" in data else None,
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
