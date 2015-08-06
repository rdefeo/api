from uuid import uuid4
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from api.logic.websocket import WebSocket as WebSocketLogic
__author__ = 'robdefeo'




class WebSocket(WebSocketHandler):
    def initialize(self, content):
        self.logic = WebSocketLogic(content=content)

    def check_origin(self, origin):
        return True

    def open(self):
        self.id = uuid4()
        # self.get_query_argument("application_id")
        self.logic.open(self)

    def on_message(self, message):
        self.logic.on_message(json_decode(message))

    def on_close(self):
        self.logic.on_close(self)