from bson import ObjectId

from api.settings import TILE_IMAGE_PATH
from prproc.url import create_product_url
from api.handlers.websocket import WebSocket as WebSocketHandler
from api.cache import FavoritesCache


class Suggestions:
    def __init__(self, product_content, favorites_cache: FavoritesCache, sender):
        self._product_content = product_content
        self._favorites_cache = favorites_cache
        self._sender = sender

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
                        "url": create_product_url(product),
                        "favorited": str(product["_id"]) in user_favorites
                    }
                )
                items.append(product)
        return items

    def get_tile(self, suggestion):
        for image in suggestion["images"]:
            if "tiles" in image:
                for tile in image["tiles"]:
                    if "width" in image and "height" in image:
                        image_scale = "width" if image["width"] > image["height"]  else "height"
                    else:
                        image_scale = "width"
                    if tile["w"] == "w-md":
                        return {
                            "image_scale": image_scale,
                            "colspan": 1,
                            "rowspan": 1 if tile["h"] == "h-md" else 2,
                            "image_url": "%s%s" % (TILE_IMAGE_PATH, tile["path"])
                        }
