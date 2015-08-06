from api.logic.generic import Generic
from api.handlers.websocket import WebSocket as WebSocketHandler


class WebSocket(Generic):
    def __init__(self, content, client_handlers):
        self._content = content
        self._client_handlers = client_handlers

    def open(self, handler: WebSocketHandler):
        if handler.id not in self._client_handlers:
            self._client_handlers[handler.id] = handler

    def on_home_page_message(self, handler, message):
        new_message_text = message["message_text"]
        self.get_detection_context(
            handler.user_id,
            handler.application_id,
            handler.session_id,
            None,
            handler.locale,
            new_message_text,
            handler.skip_mongodb_log
        )
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

    def on_close(self, handler):
        """

        :type handler: WebSocketHandler
        """
        if handler.id in self._client_handlers:
            self._client_handlers.pop(handler.id, None)
