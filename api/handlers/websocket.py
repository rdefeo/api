from uuid import uuid4
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode


class WebSocket(WebSocketHandler):
    _logic = None
    user_id = None
    id = None
    application_id = None
    session_id = None

    context_id = None
    context_rev = None
    context = None

    suggest_id = None
    offset = None
    page_size = None

    def initialize(self, content, client_handlers):
        from api.logic.websocket import WebSocket as WebSocketLogic
        self._logic = WebSocketLogic(content=content, client_handlers=client_handlers)

    def check_origin(self, origin):
        return True

    def open(self):
        self.id = uuid4()
        self.user_id = self.get_argument("user_id", None)
        self.application_id = self.get_argument("application_id", None)
        self.context_id = self.get_argument("context_id", None)
        self.session_id = self.get_argument("session_id", None)
        self.locale = self.get_argument("locale", None)
        self.page_size = 20
        self.offset = 0
        self.suggest_id = None

        self._logic.open(self)

    def on_message(self, message):
        self._logic.on_message(self, json_decode(message))

    def on_close(self):
        self._logic.on_close(self)
