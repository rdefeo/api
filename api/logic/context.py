import logging

from tornado.escape import json_encode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError

from api.settings import LOGGING_LEVEL, CONTEXT_URL


class Context:
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def post_context_message(self, context_id: str, direction: int, message_text: str, callback,
                             detection: dict = None):
        """
        Direction is 1 user 0 jemboo
        :type direction: int
        """
        self.logger.debug(
            "context_id=%s,direction=%s,message_text=%s,detection=%s",
            context_id, direction, message_text, detection
        )
        try:
            request_body = {
                "direction": direction,
                "text": message_text
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
