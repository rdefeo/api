from tornado.escape import json_decode, json_encode, url_escape
from tornado.httpclient import HTTPClient, HTTPRequest, HTTPError

from api.logic.generic import Generic
from api.handlers.websocket import WebSocket as WebSocketHandler
from api.settings import CONTEXT_URL, DETECT_URL


class WebSocket(Generic):
    def __init__(self, content, client_handlers):
        self._content = content
        self._client_handlers = client_handlers

    def open(self, handler: WebSocketHandler):
        if handler.context_id is None:
            handler.context_id, handler.context_ver = self.post_context(
                handler.user_id, handler.application_id, handler.session_id, handler.locale, handler.skip_mongodb_log
            )

        if handler.id not in self._client_handlers:
            self._client_handlers[handler.id] = handler

    def on_home_page_message(self, handler, message):
        new_message_text = message["message_text"]
        if len(new_message_text.strip()) > 0:
            detection_response_location, detection_id = self.post_detect(
                handler.user_id, handler.application_id, handler.session_id, handler.locale, new_message_text
            )
            self.post_context_message_user(handler.context_id, detection_id, new_message_text)

        else:
            raise NotImplemented()

            # context = self.get_detection_context(
            #     handler.user_id,
            #     handler.application_id,
            #     handler.session_id,
            #     None,  # TODO use the actual context id
            #     handler.locale,
            #     new_message_text,
            #     handler.skip_mongodb_log
            # )
            # pass
            # create new_context
            # go to detection if it has a query

    def on_message(self, handler: WebSocketHandler, message: dict):
        if "type" not in message:
            raise Exception("missing message type,message=%s", message)
        elif message["type"] == "home_page_message":
            self.on_home_page_message(handler, message)
        else:
            raise Exception("unknown message_type, type=%s,message=%s", message["type"], message)
        pass

    def on_close(self, handler: WebSocketHandler):
        if handler.id in self._client_handlers:
            self._client_handlers.pop(handler.id, None)

    @staticmethod
    def get_context(context_id: str) -> dict:
        http_client = HTTPClient()
        url = "%s?context_id=%s" % (CONTEXT_URL, context_id)
        context_response = http_client.fetch(HTTPRequest(url=url, method="GET"))
        http_client.close()
        return json_decode(context_response.body)

    def post_context_message_user(self, context_id: str, detection_id: str, message_text: str):
        self.post_context_message(
            context_id=context_id,
            direction=1,
            detection_id=detection_id,
            message_text=message_text
        )


    @staticmethod
    def post_context(user_id: str, application_id: str, session_id: str, locale: str, skip_mongodb_log: bool) -> dict:
        try:
            request_body = {}
            #     # this now goes at message level
            #     # if detection_response is not None:
            #     #     request_body["detection_response"] = detection_response
            url = "%s?session_id=%s&application_id=%s&locale=%s" % (
                CONTEXT_URL, session_id, application_id, locale
            )

            url += "&user_id=%s" % user_id if user_id is not None else ""
            url += "&skip_mongodb_log" % user_id if skip_mongodb_log else ""

            if skip_mongodb_log:
                url += "&skip_mongodb_log"

            http_client = HTTPClient()
            response = http_client.fetch(HTTPRequest(url=url, body=json_encode(request_body), method="POST"))
            http_client.close()

            return response["headers"]["_id"],  response["headers"]["_ver"]
        except HTTPError as e:
            raise

    @staticmethod
    def post_context_message(context_id: str, direction: int, message_text: str, detection_id: str=None):
        request_body = {
            "direction": direction,
            "text": message_text
        }
        if detection_id is not None:
            request_body["detection_id"] = detection_id

        url = "%s/%s/messages/" % (
            CONTEXT_URL, context_id
        )
        http_client = HTTPClient()
        response = http_client.fetch(HTTPRequest(url=url, body=json_encode(request_body), method="POST"))
        http_client.close()

    @staticmethod
    def post_detect(user_id: str, application_id: str, session_id: str, locale: str, query: str) -> dict:
        url = "%s?application_id=%s&session_id=%s&locale=%s&q=%s" % (
            DETECT_URL,
            application_id,
            session_id,
            locale,
            url_escape(query)
            # url_escape(json_encode(context))
        )
        if user_id is not None:
            url += "&user_id=%s" % user_id
        http_client = HTTPClient()
        response = http_client.fetch(HTTPRequest(url=url, method="POST", body=json_encode({})))
        http_client.close()
        return response.headers["Location"], response.headers["_id"]
