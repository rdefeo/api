from datetime import datetime
import logging

from tornado.escape import json_encode

from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
import dateutil.parser
from api.handlers.websocket import WebSocket as WebSocketHandler
from api.settings import LOGGING_LEVEL, CONTEXT_URL


class Context:
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def get_context_messages(self, handler: WebSocketHandler, callback) -> dict:
        try:
            if handler.context is None or handler.context["_rev"] != handler.context_rev:
                self.logger.debug(
                    "get_context_from_service,context_id=%s,_rev=%s", str(handler.context_id), handler.context_rev)
                http_client = AsyncHTTPClient()
                url = "%s/%s/messages" % (CONTEXT_URL, str(handler.context_id))
                http_client.fetch(HTTPRequest(url=url, method="GET"), callback=callback)
                http_client.close()

        except HTTPError as e:
            self.logger.error("get_context,url=%s", url)
            raise

    def post_context_message(
            self, context_id: str, direction: int, message_text: str, callback, detection: dict = None, now=None):
        """
        Direction is 1 user 0 jemboo
        :type direction: int
        """
        self.logger.debug(
            "context_id=%s,direction=%s,message_text=%s,detection=%s",
            context_id, direction, message_text, detection
        )
        now = datetime.now() if now is None else now
        try:
            request_body = {
                "direction": direction,
                "text": message_text,
                "created": now.isoformat()
            }
            if detection is not None:
                request_body["detection"] = detection

            url = "%s/%s/messages/" % (CONTEXT_URL, context_id)
            http_client = AsyncHTTPClient()
            http_client.fetch(
                HTTPRequest(url=url, method="POST", body=json_encode(request_body)),
                callback=callback
            )
            http_client.close()
        except HTTPError as e:
            self.logger.error("post_context_message,url=%s", url)
            raise
