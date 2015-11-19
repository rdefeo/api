import logging

from tornado.escape import json_decode

from api.handlers.websocket import WebSocket as WebSocketHandler
from api.logic import SenderLogic, DetectLogic, ContextLogic, SuggestLogic
from api.settings import LOGGING_LEVEL


class NewMessage:
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def __init__(self, sender: SenderLogic, detect: DetectLogic, context: ContextLogic, suggest: SuggestLogic):
        self.sender = sender
        self.new_message_text_handler = NewMessageText(self.sender, detect, context, suggest)
        self.new_message_empty_handler = NewMessageEmpty(self.sender, context, suggest)

    def on_new_message(self, handler: WebSocketHandler, message: dict, new_conversation: bool = False):
        self.sender.write_thinking_message(handler, "conversation")
        self.sender.write_thinking_message(handler, "suggestions")
        new_message_text = message["message_text"] if "message_text" in message else ""
        if len(new_message_text.strip()) > 0:
            self.new_message_text_handler.on_new_message_text(handler, message, new_message_text)
        else:
            self.new_message_empty_handler.on_new_message_empty(handler, message)


class NewMessageText:
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def __init__(self, sender: SenderLogic, detect: DetectLogic, context: ContextLogic, suggest: SuggestLogic):
        self.sender = sender
        self.detect = detect
        self.context = context
        self.suggest = suggest

    def on_new_message_text(self, handler: WebSocketHandler, message: dict, new_message_text):
        self.detect.post_detect(
            handler.user_id, handler.application_id, handler.session_id, handler.locale, new_message_text,
            lambda response: self.post_detect_callback(response, handler, message)
        )

    def post_detect_callback(self, response, handler: WebSocketHandler, message: dict):
        self.logger.debug("post_detect_callback")
        self.detect.get_detect(
            response.headers["Location"],
            lambda res: self.get_detect_callback(res, handler, message)
        )

    def decode_response(self, body):
        return json_decode(body)

    def get_detect_callback(self, response, handler_callback: WebSocketHandler, message: dict):
        self.logger.debug("get_detect_callback")
        detection_response = self.decode_response(response.body)

        self.context.post_context_message(
            handler_callback.context_id,
            1,
            message["message_text"] if "message_text" in message else "",
            callback=lambda res: self.get_context_callback(res, handler_callback, message),
            detection=detection_response
        )

        detection_chat_response = self.detect.respond_to_detection_response(handler_callback, detection_response)
        if detection_chat_response is not None:
            self.sender.write_jemboo_response_message(handler_callback, detection_chat_response)

    def get_context_callback(self, response, handler_callback: WebSocketHandler, message: dict):
        self.logger.debug("get_context_callback")
        self.context.get_context(
            handler_callback,
            lambda res: self.post_context_message_user_callback(res, handler_callback, message)
        )

    def post_context_message_user_callback(self, response, handler: WebSocketHandler, message: dict):
        self.logger.debug("post_context_message_user_callback")
        handler.context = self.decode_response(response.body)
        handler.context_rev = handler.context["_rev"]
        self.suggest.post_suggest(
            handler.user_id,
            handler.application_id,
            handler.session_id,
            handler.locale,
            handler.context,
            callback=lambda res: self.post_suggest_callback(res, handler, message)
        )

    def post_suggest_callback(self, response, handler: WebSocketHandler, message: dict):
        self.logger.debug("post_suggest_callback")
        handler.suggest_id = response.headers["_id"]
        self.suggest.write_new_suggestion(handler)


class NewMessageEmpty:
    def __init__(self, sender: SenderLogic, context: ContextLogic, suggest: SuggestLogic):
        self.sender = sender
        self.context = context
        self.suggest = suggest

    def on_new_message_empty(self, handler: WebSocketHandler, message: dict):
        self.context.get_context(
            handler,
            callback=lambda res: self.get_context_callback(res, handler, message)
        )

    def get_context_callback(self, response, handler: WebSocketHandler, message: dict):
        handler.context = json_decode(response.body)
        handler.context_rev = handler.context["_rev"]
        if not any(x for x in handler.context["entities"] if x["source"] == "detection"):
            handler.suggest_id = self.suggest.post_suggest(
                handler.user_id, handler.application_id, handler.session_id, handler.locale, handler.context,
                callback=lambda res: self.post_suggest_callback(res, handler, message)
            )
        else:
            # TODO No idea what to do here
            pass

    def post_suggest_callback(self, response, handler: WebSocketHandler, message: dict):
        handler.suggest_id = response.headers["_id"]
        self.suggest.write_new_suggestion(handler)

