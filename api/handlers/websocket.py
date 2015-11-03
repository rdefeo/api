from uuid import uuid4

from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode

from api.handlers.extractors import ParamExtractor, WebSocketCookieExtractor


class WebSocket(WebSocketHandler):
    _param_extractor = None
    _cookie_extractor = None
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

    def initialize(self, product_content, client_handlers, user_info_cache):
        from api.logic.websocket import WebSocket as WebSocketLogic
        self._logic = WebSocketLogic(product_content=product_content, client_handlers=client_handlers,
                                     user_info_cache=user_info_cache)
        self._param_extractor = ParamExtractor(self)
        self._cookie_extractor = WebSocketCookieExtractor(self)

    def check_origin(self, origin):
        return True

    def open(self):
        self.id = uuid4()
        self.user_id = self._cookie_extractor.user_id()
        self.application_id = self._cookie_extractor.application_id()
        self.session_id = self._cookie_extractor.session_id()
        self.context_id = self._param_extractor.context_id()
        self.suggest_id = self._param_extractor.suggest_id()
        self.locale = self._param_extractor.locale()
        self.page_size = 20

        self._logic.open(self)

    def on_message(self, message):
        self._logic.on_message(self, json_decode(message))
        if self.user_id is None:  # maybe they logged in
            self.user_id = self._cookie_extractor.user_id()
        

    def on_close(self):
        self._logic.on_close(self)
