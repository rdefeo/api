from api.logic.generic import Generic

__author__ = 'robdefeo'

client_handlers = {}


class WebSocket(Generic):
    def __init__(self, content):
        self._content = content

    def open(self, handler):
        if handler.id not in client_handlers:
            client_handlers[handler.id] = handler

    def on_message(self, message):
        """
        Minimum payload
        :param message:
        {
            'type': "valid_type"
        }
        :return:
        """
        if message["type"] == "home_page_message":
            self.get_detection_context(

            )
            # create new_context
            # go to detection if it has a query
            pass
        else:
            raise Exception("unknown message type,%s,message", message["type"], message)
        pass

    def on_close(self, handler):
        if handler.id in client_handlers:
            client_handlers.pop(handler.id, None)
