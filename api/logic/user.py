from json import dumps
import logging
from bson import ObjectId
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
from api.settings import LOGGING_LEVEL, CONTEXT_URL, USER_URL
from api.handlers.websocket import WebSocket as WebSocketHandler


class User:
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def __init__(self, user_info_cache):
        self.user_info = user_info_cache

    def get_profile_picture(self, _id: ObjectId):
        user_info = self.user_info.get(_id)
        if user_info is not None and "profile_photo_url" in user_info:
            return user_info["profile_photo_url"]
        else:
            return None

    def put_favorite(self, handler: WebSocketHandler, user_id: str, product_id: str):
        def put_favorite_callback(response, handler):
            self.logger.debug("put_favorite_completed")

        self.logger.debug(
            "user_id=%s,product_id=%s",
            user_id, product_id
        )
        try:
            url = "%s/%s/favorite/%s" % (USER_URL, user_id, product_id)

            http_client = AsyncHTTPClient()
            http_client.fetch(
                HTTPRequest(url=url, body=dumps({}), method="PUT"),
                callback=lambda res: put_favorite_callback(res, handler)
            )
            http_client.close()

        except HTTPError as e:
            self.logger.error("put_favorite,url=%s", url)
            raise

    def get_favorites(self):
        # TODO its own seperate logic i think?????
        pass
