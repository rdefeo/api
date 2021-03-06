import logging

from api.logic.context import Context
from api.settings import LOGGING_LEVEL
from api.handlers.websocket import WebSocket as WebSocketHandler


class Sender:
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def __init__(self, client_handlers):
        self._client_handlers = client_handlers
        self.context = Context()

    def write_thinking_message(self, handler: WebSocketHandler, thinking_mode: str, meta_data: dict = None):
        message = {
            "type": "start_thinking",
            "thinking_mode": thinking_mode
        }

        if meta_data is not None:
            message["meta_data"] = meta_data

        self.write_to_context_handlers(handler, message)

    def write_jemboo_response_message(self, handler: WebSocketHandler, message: dict):
        message["type"] = "jemboo_chat_response"
        message["direction"] = 0  # jemboo

        # TODO store this message in the context too
        self.context.post_context_message(
            handler.context_id,
            message["direction"],
            message["display_text"],
            callback=lambda res: self.post_suggest_callback(res, handler, message)
        )

    def post_suggest_callback(self, response, handler: WebSocketHandler, message: dict):
        self.write_to_context_handlers(handler, message)

    def write_to_context_handlers(self, handler: WebSocketHandler, message: dict):
        handlers = self._client_handlers[str(handler.context_id)].values()
        self.logger.info(
            "write message context_id=%s,type=%s,handlers_length=%s",
            str(handler.context_id), message["type"], len(handlers))
        for x in handlers:
            self.logger.info("write message context_id=%s,type=%s,handler_id=%s",
                             str(handler.context_id), message["type"],
                             x.id)
            x.write_message(message)
