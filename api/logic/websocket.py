from logging import getLogger

from bson.json_util import dumps, loads
from tornado.escape import json_decode, json_encode, url_escape
from tornado.httpclient import HTTPClient, HTTPRequest, HTTPError

from api.content import Content
from api.logic import DetectLogic
from api.handlers.websocket import WebSocket as WebSocketHandler
from api.settings import CONTEXT_URL, DETECT_URL, SUGGEST_URL


class WebSocket:
    logger = getLogger(__name__)
    detect = DetectLogic()

    def __init__(self, content: Content, client_handlers):
        self._content = content
        self._client_handlers = client_handlers

    def open(self, handler: WebSocketHandler):
        if handler.context_id is None:
            handler.context_id, handler.context_rev = self.post_context(
                handler.user_id, handler.application_id, handler.session_id, handler.locale
            )

        if handler.id not in self._client_handlers:
            self._client_handlers[handler.id] = handler

        handler.write_message(
            {
                "type": "connection_opened",
                "context_id": str(handler.context_id)
            }
        )

    def write_thinking_message(self, handler: WebSocketHandler, thinking_mode: str, meta_data: dict=None):
        message = {
            "type": "start_thinking",
            "thinking_mode": thinking_mode
        }

        if meta_data is not None:
            message["meta_data"] = meta_data

        handler.write_message(message)

    def write_suggestion_items(self, handler: WebSocketHandler, suggestion_items_response: dict):
        handler.write_message(
            {
                "type": "suggestion_items",
                "offset": suggestion_items_response["offset"],
                "items": self.fill_suggestions(suggestion_items_response["items"])
            }
        )

    def fill_suggestions(self, suggestions):
        items = []
        for suggestion in suggestions:
            new_suggestion = self._content.get_product(suggestion["_id"])
            if new_suggestion is not None:
                new_suggestion["tile"] = self.get_tile(new_suggestion)
                new_suggestion["score"] = suggestion["score"]
                new_suggestion["reasons"] = suggestion["reasons"]
                new_suggestion["_id"] = str(suggestion["_id"])
                new_suggestion["position"] = suggestion["index"]
                items.append(new_suggestion)
        return items

    def get_tile(self, suggestion):
        for image in suggestion["images"]:
            if "tiles" in image:
                for tile in image["tiles"]:
                    if tile["w"] == "w-md":
                        return {
                            "colspan": 1,
                            "rowspan": 1 if tile["h"] == "h-md" else 2,
                            "image_url": tile["path"]
                        }

    def on_next_page_message(self, handler: WebSocketHandler, message: dict):
        suggestion_items_response, handler.offset = self.get_suggestion_items(
            handler.user_id,
            handler.application_id,
            handler.session_id,
            handler.locale,
            handler.suggest_id,
            handler.page_size,
            handler.offset
        )

        self.write_suggestion_items(handler, suggestion_items_response)

    def on_view_product_details_message(self, handler: WebSocketHandler, message: dict):
        handler.context_rev = self.post_context_feedback(
            handler.context_id,
            handler.user_id,
            handler.application_id,
            handler.session_id,
            message["product_id"],
            message["feedback_type"],
            message["meta_data"] if "meta_data" in message else None
        )
        pass

    def on_new_message(self, handler: WebSocketHandler, message: dict, new_conversation: bool=False):
        new_message_text = message["message_text"]
        if len(new_message_text.strip()) > 0:
            self.write_thinking_message(handler, "conversation")
            self.write_thinking_message(handler, "suggestions")

            handler.offset = 0
            detection_response_location = self.post_detect(
                handler.user_id, handler.application_id, handler.session_id, handler.locale, new_message_text
            )
            detection_response = self.get_detect(detection_response_location)
            # TODO 25 non detected items

            handler.context_rev = self.post_context_message_user(
                handler.context_id,
                detection_response,
                new_message_text
            )

            handler.suggest_id = self.post_suggest(
                handler.user_id, handler.application_id, handler.session_id, handler.locale, self.get_context(handler)
            )

            suggestion_items_response, handler.offset = self.get_suggestion_items(
                handler.user_id,
                handler.application_id,
                handler.session_id,
                handler.locale,
                handler.suggest_id,
                handler.page_size,
                handler.offset
            )

            self.write_suggestion_items(handler, suggestion_items_response)

        else:
            raise NotImplementedError()

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
            self.on_new_message(handler, message, new_conversation=True)
        elif message["type"] == "new_message":
            self.on_new_message(handler, message, new_conversation=False)
        elif message["type"] == "next_page":
            self.on_next_page_message(handler, message)
        elif message["type"] == "view_product_details":
            self.on_view_product_details_message(handler, message)
        else:
            raise Exception("unknown message_type, type=%s,message=%s", message["type"], message)
        pass

    def on_close(self, handler: WebSocketHandler):
        if handler.id in self._client_handlers:
            self._client_handlers.pop(handler.id, None)

    def get_context(self, handler: WebSocketHandler) -> dict:
        try:
            if handler.context is None or handler.context["_rev"] != handler.context_rev:
                http_client = HTTPClient()
                url = "%s/%s" % (CONTEXT_URL, handler.context_id)
                url += "?_rev=%s" % handler.context_rev if handler.context_rev is not None else ""
                context_response = http_client.fetch(HTTPRequest(url=url, method="GET"))
                http_client.close()
                handler.context = json_decode(context_response.body)
                handler.context_rev = handler.context["_rev"]

            return handler.context
        except HTTPError as e:
            self.logger.error("get_context,url=%s", url)
            raise

    @staticmethod
    def post_context(user_id: str, application_id: str, session_id: str, locale: str) -> dict:
        try:
            request_body = {}
            #     # this now goes at message level
            #     # if detection_response is not None:
            #     #     request_body["detection_response"] = detection_response
            url = "%s?session_id=%s&application_id=%s&locale=%s" % (
                CONTEXT_URL, session_id, application_id, locale
            )

            url += "&user_id=%s" % user_id if user_id is not None else ""

            http_client = HTTPClient()
            response = http_client.fetch(HTTPRequest(url=url, body=json_encode(request_body), method="POST"))
            http_client.close()

            return response.headers["_id"], response.headers["_rev"]
        except HTTPError as e:
            raise

    def post_context_message_user(self, context_id: str, detection: dict, message_text: str):
        return self.post_context_message(
            context_id=context_id,
            direction=1,
            detection=detection,
            message_text=message_text
        )

    @staticmethod
    def post_context_message(context_id: str, direction: int, message_text: str, detection: dict=None):
        try:
            request_body = {
                "direction": direction,
                "text": message_text
            }
            if detection is not None:
                request_body["detection"] = detection

            url = "%s/%s/messages/" % (CONTEXT_URL, context_id)
            http_client = HTTPClient()
            response = http_client.fetch(HTTPRequest(url=url, body=dumps(request_body), method="POST"))
            http_client.close()
            return response.headers["_rev"]
        except HTTPError as e:
            pass
            raise

    @staticmethod
    def post_context_feedback(context_id: str, user_id: str, application_id: str, session_id: str,
                              product_id: str, _type: str, meta_data: dict=None):
        try:
            request_body = {
            }
            if meta_data is not None:
                request_body["meta_data"] = meta_data

            url = "%s/%s/feedback/?application_id=%s&session_id=%s&product_id=%s&type=%s" % (
                CONTEXT_URL, context_id, application_id, session_id, product_id, _type
            )
            url += "&user_id=%s" if user_id is not None else ""

            http_client = HTTPClient()
            response = http_client.fetch(HTTPRequest(url=url, body=dumps(request_body), method="POST"))
            http_client.close()
            return response.headers["_rev"]
        except HTTPError as e:
            pass
            raise

    def get_detect(self, location: str) -> dict:
        try:
            http_client = HTTPClient()
            url = "%s%s" % (DETECT_URL, location)
            detect_response = http_client.fetch(HTTPRequest(url=url, method="GET"))
            http_client.close()
            return json_decode(detect_response.body)
        except HTTPError as e:
            self.logger.error("get_detect,url=%s", url)
            raise

    @staticmethod
    def post_detect(user_id: str, application_id: str, session_id: str, locale: str, query: str) -> str:
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
        return response.headers["Location"]

    @staticmethod
    def post_suggest(user_id: str, application_id: str, session_id: str, locale: str, context: dict) -> str:
        try:
            request_body = {
                "context": context
            }

            url = "%s?session_id=%s&application_id=%s&locale=%s" % (
                SUGGEST_URL, session_id, application_id, locale
            )

            url += "&user_id=%s" % user_id if user_id is not None else ""

            http_client = HTTPClient()
            response = http_client.fetch(HTTPRequest(url=url, body=dumps(request_body), method="POST"))
            http_client.close()

            return response.headers["_id"]
        except HTTPError as e:
            raise

    @staticmethod
    def get_suggestion_items(user_id: str, application_id: str, session_id: str, locale: str, suggestion_id: str,
                             page_size: int, offset: int) -> (dict, int):
        http_client = HTTPClient()
        url = "%s/%s/items?session_id=%s&application_id=%s&locale=%s&page_size=%s&offset=%s" % (
            SUGGEST_URL, suggestion_id, session_id, application_id, locale, page_size, offset
        )

        url += "&user_id=%s" % user_id if user_id is not None else ""

        suggest_response = http_client.fetch(HTTPRequest(url=url, method="GET"))
        http_client.close()
        return loads(suggest_response.body.decode("utf-8")), suggest_response.headers["next_offset"]
