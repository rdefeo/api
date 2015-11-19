import logging
from bson import ObjectId

from bson.json_util import dumps, loads
from tornado.escape import json_decode, json_encode, url_escape
from tornado.httpclient import HTTPClient, HTTPRequest, HTTPError, AsyncHTTPClient

from api.cache import ProductDetailCache
from api.logic import DetectLogic, UserLogic, ContextLogic
from api.handlers.websocket import WebSocket as WebSocketHandler
from api.logic.message_response import MessageResponse
from api.logic.sender import Sender
from api.logic.suggestions import Suggestions
from api.settings import CONTEXT_URL, DETECT_URL, SUGGEST_URL, LOGGING_LEVEL

from api.logic.incoming_message_handlers import NextPageMessageHandler


class WebSocket:
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def __init__(self, product_content: ProductDetailCache, client_handlers, user_info_cache, favorites_cache):
        self.sender = Sender(client_handlers)
        self.context = ContextLogic()
        self.detect = DetectLogic(self.sender)
        self.message_response = MessageResponse()
        self.suggestions = Suggestions(product_content=product_content, sender=self.sender, favorites_cache=favorites_cache)
        self.user = UserLogic(user_info_cache=user_info_cache, favorites_cache=favorites_cache)

        self.next_page_message_handler = NextPageMessageHandler(self.suggestions)

        self._client_handlers = client_handlers


    def open(self, handler: WebSocketHandler):
        self.logger.debug(
            "context_id=%s,suggestion_id=%s",
            str(handler.context_id), handler.suggest_id
        )

        if handler.context_id is None:
            handler.context_id, handler.context_rev = self.post_context(
                handler.user_id, handler.application_id, handler.session_id, handler.locale
            )
            new_context = True
        else:
            new_context = False

        if str(handler.context_id) not in self._client_handlers:
            self._client_handlers[str(handler.context_id)] = {}

        if handler.id not in self._client_handlers[str(handler.context_id)]:
            self.logger.debug("add handler, context_id=%s,handler_id=%s", str(handler.context_id), handler.id)
            self._client_handlers[str(handler.context_id)][handler.id] = handler

        self.sender.write_to_context_handlers(
            handler,
            {
                "type": "connection_opened",
                "context_id": str(handler.context_id)
            }
        )

        if new_context:
            def post_context_callback(response, handler):
                self.logger.debug("post_context_message")

            self.context.post_context_message(
                handler.context_id,
                0,
                "Hi, how can I help you?",
                callback=lambda res: post_context_callback(res, handler)
            )

    def on_close(self, handler: WebSocketHandler):
        handler_id_in_client_handlers = str(handler.context_id) in self._client_handlers
        if handler_id_in_client_handlers and handler.id in self._client_handlers[str(handler.context_id)]:
            self.logger.debug(
                "remove_handler,close_code=%s,context_id=%s,context_rev=%s,handler_id=%s",
                handler.close_code, str(handler.context_id), str(handler.context_rev), handler.id
            )
            self._client_handlers[str(handler.context_id)].pop(handler.id, None)

    def write_jemboo_response_message(self, handler: WebSocketHandler, message: dict):
        message["type"] = "jemboo_chat_response"
        message["direction"] = 0  # jemboo
        # TODO store this message in the context too

        self.sender.write_to_context_handlers(handler, message)

    def write_thinking_message(self, handler: WebSocketHandler, thinking_mode: str, meta_data: dict = None):
        message = {
            "type": "start_thinking",
            "thinking_mode": thinking_mode
        }

        if meta_data is not None:
            message["meta_data"] = meta_data

        self.sender.write_to_context_handlers(handler, message)

    def write_new_suggestion(self, handler: WebSocketHandler):
        self.sender.write_to_context_handlers(
            handler,
            {
                "type": "new_suggestion",
                "suggest_id": str(handler.suggest_id)
            }
        )

    def on_load_conversation_messages(self, handler: WebSocketHandler, message: dict):
        self.context.get_context_messages(
            handler,
            callback=lambda res: get_context_messages_callback(res, handler)
        )

        def get_context_messages_callback(response, handler):
            profile_picture_url = self.user.get_profile_picture(handler.user_id)
            messages = [
                {
                    "direction": x["direction"],
                    "display_text": x["text"]
                } for x in loads(response.body.decode("utf-8"))["messages"]
                ]
            if profile_picture_url is not None:
                for x in messages:
                    if x["direction"] == 1:  # user
                        x["profile_picture_url"] = profile_picture_url

            self.sender.write_to_context_handlers(
                handler,
                {
                    "type": "conversation_messages",
                    "messages": messages
                }
            )

    # def on_next_page_message(self, handler: WebSocketHandler, message: dict):
    #     self.get_suggestion_items(
    #         handler.user_id,
    #         handler.application_id,
    #         handler.session_id,
    #         handler.locale,
    #         message["suggest_id"],
    #         handler.page_size,
    #         message["offset"],
    #         callback=lambda res: get_suggestion_items_callback(res, handler, message)
    #     )
    #
    #     def get_suggestion_items_callback(response, handler_callback: WebSocketHandler, message: dict):
    #         suggestion_items_response = loads(response.body.decode("utf-8"))
    #         next_offset = response.headers["next_offset"]
    #         self.suggestions.write_suggestion_items(handler, suggestion_items_response, message["offset"], next_offset)

    def on_favorite_product_delete_message(self, handler: WebSocketHandler, message: dict):
        self.user.delete_favorite(handler, ObjectId(message["user_id"]), ObjectId(message["product_id"]))

    def on_favorite_product_save_message(self, handler: WebSocketHandler, message: dict):
        self.user.put_favorite(handler, ObjectId(message["user_id"]), ObjectId(message["product_id"]))

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

    def on_new_message(self, handler: WebSocketHandler, message: dict, new_conversation: bool = False):
        self.write_thinking_message(handler, "conversation")
        self.write_thinking_message(handler, "suggestions")
        new_message_text = message["message_text"] if "message_text" in message else ""
        if len(new_message_text.strip()) > 0:
            self.on_new_message_text(handler, message, new_message_text)
        else:
            self.on_new_message_empty(handler, message)

    def on_new_message_empty(self, handler: WebSocketHandler, message: dict):
        def get_context_callback(response, handler: WebSocketHandler, message: dict):
            handler.context = json_decode(response.body)
            handler.context_rev = handler.context["_rev"]
            if not any(x for x in handler.context["entities"] if x["source"] == "detection"):
                handler.suggest_id = self.post_suggest(
                    handler.user_id, handler.application_id, handler.session_id, handler.locale, handler.context,
                    callback=lambda res: post_suggest_callback(res, handler, message)
                )
            else:
                # TODO No idea what to do here
                pass

        def post_suggest_callback(response, handler: WebSocketHandler, message: dict):
            handler.suggest_id = response.headers["_id"]
            self.write_new_suggestion(handler)

        self.get_context(
            handler,
            callback=lambda res: get_context_callback(res, handler, message)
        )

    def on_new_message_text(self, handler: WebSocketHandler, message: dict, new_message_text):
        def post_detect_callback(response, handler: WebSocketHandler, message: dict):
            self.logger.debug("post_detect_callback")
            self.get_detect(
                response.headers["Location"],
                lambda res: get_detect_callback(res, handler, message)
            )

        def get_detect_callback(response, handler_callback: WebSocketHandler, message: dict):
            self.logger.debug("get_detect_callback")
            detection_response = json_decode(response.body)
            self.context.post_context_message(
                handler_callback.context_id,
                1,
                message["message_text"] if "message_text" in message else "",
                lambda res: get_context_callback(res, handler_callback, message),
                detection=detection_response
            )

            detection_chat_response = self.detect.respond_to_detection_response(handler_callback, detection_response)
            if detection_chat_response is not None:
                self.sender.write_jemboo_response_message(handler_callback, detection_chat_response)

        def get_context_callback(response, handler_callback: WebSocketHandler, message: dict):
            self.logger.debug("get_context_callback")
            self.get_context(
                handler_callback,
                lambda res: post_context_message_user_callback(res, handler_callback, message)
            )

        def post_context_message_user_callback(response, handler: WebSocketHandler, message: dict):
            self.logger.debug("post_context_message_user_callback")
            handler.context = json_decode(response.body)
            handler.context_rev = handler.context["_rev"]
            self.post_suggest(
                handler.user_id, handler.application_id, handler.session_id,
                handler.locale,
                handler.context,
                callback=lambda res: post_suggest_callback(res, handler, message)
            )

        def post_suggest_callback(response, handler: WebSocketHandler, message: dict):
            self.logger.debug("post_suggest_callback")
            handler.suggest_id = response.headers["_id"]
            self.write_new_suggestion(handler)

        self.post_detect(
            handler.user_id, handler.application_id, handler.session_id, handler.locale, new_message_text,
            lambda response: post_detect_callback(response, handler, message)
        )

    def on_message(self, handler: WebSocketHandler, message: dict):
        if "type" not in message:
            raise Exception("missing message type,message=%s", message)

        self.logger.debug("message_type=%s,message=%s", message["type"], message)

        if message["type"] == "home_page_message":
            self.on_new_message(handler, message, new_conversation=True)
        elif message["type"] == "new_message":
            self.on_new_message(handler, message, new_conversation=False)
        elif message["type"] == "next_page":
            self.next_page_message_handler.on_next_page_message(handler, message)
        elif message["type"] == "view_product_details":
            self.on_view_product_details_message(handler, message)
        elif message["type"] == "load_conversation_messages":
            self.on_load_conversation_messages(handler, message)
        elif message["type"] == "favorite_product_save":
            self.on_favorite_product_save_message(handler, message)
        elif message["type"] == "favorite_product_delete":
            self.on_favorite_product_delete_message(handler, message)
        else:
            raise Exception("unknown message_type, type=%s,message=%s", message["type"], message)
        pass

    def get_context(self, handler: WebSocketHandler, callback):
        try:
            if handler.context is None or handler.context["_rev"] != handler.context_rev:
                self.logger.debug(
                    "get_context_from_service,context_id=%s,_rev=%s", str(handler.context_id), handler.context_rev)
                url = "%s/%s" % (CONTEXT_URL, str(handler.context_id))
                url += "?_rev=%s" % handler.context_rev if handler.context_rev is not None else ""
                http_client = AsyncHTTPClient()
                http_client.fetch(HTTPRequest(url=url, method="GET"), callback=callback)
                http_client.close()

        except HTTPError as e:
            self.logger.error("get_context,url=%s", url)
            raise

    def post_context(self, user_id: str, application_id: str, session_id: str, locale: str) -> dict:
        self.logger.debug(
            "user_id=%s,application_id=%s,session_id=%s,locale=%s",
            user_id, application_id, session_id, locale
        )
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

    def post_context_feedback(self, context_id: str, user_id: str, application_id: str, session_id: str,
                              product_id: str, _type: str, meta_data: dict = None):
        self.logger.debug(
            "context_id=%s,user_id=%s,application_id=%s,session_id=%s,product_id=%s,"
            "_type=%s,meta_data=%s",
            context_id, user_id, application_id, session_id, product_id, _type, meta_data
        )
        try:
            url = "%s/%s/feedback/?application_id=%s&session_id=%s&product_id=%s&type=%s" % (
                CONTEXT_URL, context_id, application_id, session_id, product_id, _type
            )
            url += "&user_id=%s" if user_id is not None else ""

            request_body = {
            }
            if meta_data is not None:
                request_body["meta_data"] = meta_data

            http_client = HTTPClient()
            response = http_client.fetch(HTTPRequest(url=url, body=dumps(request_body), method="POST"))
            http_client.close()
            return response.headers["_rev"]
        except HTTPError as e:
            self.logger.error("post_context_feedback,url=%s", url)
            raise

    def get_detect(self, location: str, callback) -> dict:
        self.logger.debug("location=%s", location)
        try:
            http_client = AsyncHTTPClient()
            url = "%s%s" % (DETECT_URL, location)
            http_client.fetch(HTTPRequest(url=url, method="GET"), callback=callback)
            http_client.close()
        except HTTPError as e:
            self.logger.error("get_detect,url=%s", url)
            raise

    def post_detect(self, user_id: str, application_id: str, session_id: str, locale: str, query: str, callback) -> str:
        self.logger.debug(
            "user_id=%s,application_id=%s,session_id=%s,locale=%s,query=%s",
            user_id, application_id, session_id, locale, query
        )

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
        http_client = AsyncHTTPClient()
        http_client.fetch(
            HTTPRequest(url=url, method="POST", body=json_encode({})),
            callback=callback
        )
        http_client.close()

    def post_suggest(self, user_id: str, application_id: str, session_id: str, locale: str, context: dict,
                     callback) -> str:
        self.logger.debug(
            "user_id=%s,application_id=%s,session_id=%s,locale=%s,"
            "context=%s",
            user_id, application_id, session_id, locale, context
        )

        try:
            request_body = {
                "context": context
            }

            url = "%s?session_id=%s&application_id=%s&locale=%s" % (
                SUGGEST_URL, session_id, application_id, locale
            )

            url += "&user_id=%s" % user_id if user_id is not None else ""

            http_client = AsyncHTTPClient()
            http_client.fetch(HTTPRequest(url=url, body=dumps(request_body), method="POST"), callback=callback)
            http_client.close()

        except HTTPError as e:
            self.logger.error("url=%s", url)
            raise

    # def get_suggestion_items(self, user_id: str, application_id: str, session_id: str, locale: str, suggestion_id: str,
    #                          page_size: int, offset: int, callback):
    #     self.logger.debug(
    #         "user_id=%s,application_id=%s,session_id=%s,locale=%s,"
    #         "suggestion_id=%s,page_size=%s,offset=%s",
    #         user_id, application_id, session_id, locale, suggestion_id, page_size, offset
    #     )
    #     try:
    #         http_client = AsyncHTTPClient()
    #         url = "%s/%s/items?session_id=%s&application_id=%s&locale=%s&page_size=%s&offset=%s" % (
    #             SUGGEST_URL, suggestion_id, session_id, application_id, locale, page_size, offset
    #         )
    #
    #         url += "&user_id=%s" % user_id if user_id is not None else ""
    #
    #         http_client.fetch(HTTPRequest(url=url, method="GET"), callback=callback)
    #         http_client.close()
    #
    #     except HTTPError as e:
    #         self.logger.error("url=%s", url)
    #         raise
