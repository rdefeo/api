from uuid import uuid4
from tornado.websocket import WebSocketHandler

__author__ = 'robdefeo'

clients = {}


class Websocket(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        self._id = uuid4()
        if self._id not in clients:
            clients[self._id] = self

    def on_message(self, message):
        pass
        # self.write_message()
        # msg = json.loads(message)
        # self.w
        # clients["d"].wr
        # msg['username'] = self.__rh.client_info[self.__clientID]['nick']
        # pmessage = json.dumps(msg)
        # rconns = self.__rh.roomate_cwsconns(self.__clientID)
        # for conn in rconns:
        #     conn.write_message(pmessage)

    def on_close(self):
        if self._id in clients:
            clients.pop(self._id, None)