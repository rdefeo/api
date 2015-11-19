import logging

from bson.json_util import dumps

from bson import ObjectId

from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError

from api.settings import TILE_IMAGE_PATH, SUGGEST_URL, LOGGING_LEVEL
from api.handlers.websocket import WebSocket as WebSocketHandler
from api.cache import FavoritesCache
from api.logic.sender import Sender as SenderLogic


class Suggestions:
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def __init__(self, product_content, favorites_cache: FavoritesCache, sender: SenderLogic):
        from prproc.url import create_product_url
        self.create_product_url = create_product_url
        self._product_content = product_content
        self._favorites_cache = favorites_cache
        self._sender = sender

    def write_new_suggestion(self, handler: WebSocketHandler):
        self._sender.write_to_context_handlers(
            handler,
            {
                "type": "new_suggestion",
                "suggest_id": str(handler.suggest_id)
            }
        )

    def write_suggestion_items(self, handler: WebSocketHandler, suggestion_items_response: dict, offset: int,
                               next_offset: int):
        self._sender.write_to_context_handlers(
            handler,
            {
                "type": "suggestion_items",
                "next_offset": next_offset,
                "offset": offset,
                "suggest_id": str(handler.suggest_id),
                "items": self.fill(suggestion_items_response["items"], handler.user_id)
            }
        )

    def get_suggestion_items(self, user_id: str, application_id: str, session_id: str, locale: str, suggestion_id: str,
                             page_size: int, offset: int, callback):
        self.logger.debug(
            "user_id=%s,application_id=%s,session_id=%s,locale=%s,"
            "suggestion_id=%s,page_size=%s,offset=%s",
            user_id, application_id, session_id, locale, suggestion_id, page_size, offset
        )
        url = "%s/%s/items?session_id=%s&application_id=%s&locale=%s&page_size=%s&offset=%s" % (
            SUGGEST_URL, suggestion_id, session_id, application_id, locale, page_size, offset
        )
        url += "&user_id=%s" % user_id if user_id is not None else ""

        try:
            http_client = AsyncHTTPClient()

            http_client.fetch(HTTPRequest(url=url, method="GET"), callback=callback)
            http_client.close()

        except HTTPError:
            self.logger.error("url=%s", url)
            raise

    def post_suggest(self, user_id: str, application_id: str, session_id: str, locale: str, context: dict,
                     callback) -> str:
        self.logger.debug(
            "user_id=%s,application_id=%s,session_id=%s,locale=%s,"
            "context=%s",
            user_id, application_id, session_id, locale, context
        )

        url = "%s?session_id=%s&application_id=%s&locale=%s" % (
            SUGGEST_URL, session_id, application_id, locale
        )
        url += "&user_id=%s" % user_id if user_id is not None else ""

        try:
            request_body = {
                "context": context
            }

            http_client = AsyncHTTPClient()
            http_client.fetch(HTTPRequest(url=url, body=dumps(request_body), method="POST"), callback=callback)
            http_client.close()

        except HTTPError:
            self.logger.error("url=%s", url)
            raise

    def fill(self, suggestions, user_id: ObjectId):
        if user_id is None:
            user_favorites = []
        else:
            # current_user_favorites = self._favorites_cache.get(user_id)
            # user_favorites = current_user_favorites if current_user_favorites is not None else {}
            user_favorites = self._favorites_cache.get(user_id)

        items = []
        for suggestion in suggestions:
            product = self._product_content.get(suggestion["_id"])
            if product is not None:
                product.update(
                    {
                        "tile": self.get_tile(product),
                        "score": suggestion["score"],
                        "reasons": suggestion["reasons"],
                        "_id": str(product["_id"]),
                        "position": suggestion["index"],
                        "url": self.create_product_url(product),
                        "favorited": str(product["_id"]) in user_favorites
                    }
                )
                items.append(product)
        return items

    @staticmethod
    def get_tile(suggestion):
        for image in suggestion["images"]:
            if "tiles" in image:
                for tile in image["tiles"]:
                    if "width" in image and "height" in image:
                        image_scale = "width" if image["width"] > image["height"] else "height"
                    else:
                        image_scale = "width"
                    if tile["w"] == "w-md":
                        return {
                            "image_scale": image_scale,
                            "colspan": 1,
                            "rowspan": 1 if tile["h"] == "h-md" else 2,
                            "image_url": "%s%s" % (TILE_IMAGE_PATH, tile["path"])
                        }
