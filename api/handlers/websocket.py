from uuid import uuid4
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from api.handlers.extractors import ParamExtractor


class WebSocket(WebSocketHandler):
    _param_extractor = None
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
        self._param_extractor = ParamExtractor(self)

    def check_origin(self, origin):
        return True

    def open(self):
        self.id = uuid4()
        self.user_id = self._param_extractor.user_id()
        self.application_id = self._param_extractor.application_id()
        self.context_id = self._param_extractor.context_id()
        self.session_id = self._param_extractor.session_id()
        self.locale = self._param_extractor.locale()
        self.page_size = 20
        self.offset = 0
        self.suggest_id = None

        self._logic.open(self)

    def on_message(self, message):
        self._logic.on_message(self, json_decode(message))

    def on_close(self):
        self._logic.on_close(self)
