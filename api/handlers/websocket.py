from uuid import uuid4
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode


class WebSocket(WebSocketHandler):
    user_id = None
    id = None
    application_id = None
    session_id = None
    skip_mongodb_log = None

    def initialize(self, content, client_handlers):
        from api.logic.websocket import WebSocket as WebSocketLogic
        self.logic = WebSocketLogic(content=content, client_handlers=client_handlers)

    def check_origin(self, origin):
        return True

    def open(self):
        self.id = uuid4()
        self.user_id = self.get_argument("user_id", None)
        self.application_id = self.get_argument("application_id", None)
        # context_id = self.get_argument("context_id", None)
        self.session_id = self.get_argument("session_id", None)
        self.locale = self.get_argument("locale", None)
        self.skip_mongodb_log = self.get_argument("skip_mongodb_log", None) is not None

        self.logic.open(self)

    def on_message(self, message):
        self.logic.on_message(self, json_decode(message))

    def on_close(self):
        self.logic.on_close(self)