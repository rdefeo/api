from tornado.escape import json_decode
from tornado.httpclient import HTTPClient, HTTPRequest
from api.logic.generic import Generic
from api.handlers.websocket import WebSocket as WebSocketHandler
from api.settings import CONTEXT_URL


class WebSocket(Generic):
    def __init__(self, content, client_handlers):
        self._content = content
        self._client_handlers = client_handlers

    def open(self, handler: WebSocketHandler):
        if handler.context_id is None:
            # TOOD 31 no context ID so make a context and store it
            raise NotImplementedError()
            pass
        else:
            handler.context = self.get_context(handler.context_id)

        if handler.id not in self._client_handlers:
            self._client_handlers[handler.id] = handler

    def on_home_page_message(self, handler, message):
        new_message_text = message["message_text"]
        if len(new_message_text.strip()) > 0:
            detection_response = self.get_wit_detection(
                handler.user_id, handler.application_id, handler.session_id, handler.locale, new_message_text, None)

        else:
            raise NotImplemented()

            # context = self.get_detection_context(
            #     handler.user_id,
            #     handler.application_id,
            #     handler.session_id,
            #     None,  # TODO use the actual context id
            #     handler.locale,
            #     new_message_text,
            #     handler.skip_mongodb_log
            # )
            # pass
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

    def on_close(self, handler: WebSocketHandler):
        if handler.id in self._client_handlers:
            self._client_handlers.pop(handler.id, None)

    @staticmethod
    def get_context(context_id: str) -> dict:
        http_client = HTTPClient()
        url = "%s?context_id=%s" % (CONTEXT_URL, context_id)
        context_response = http_client.fetch(
            HTTPRequest(
                url=url,
                method="GET"
            )
        )
        http_client.close()
        return json_decode(context_response.body)

    def post_context(self):
        request_body = {}
        # this now goes at message level
        # if detection_response is not None:
        #     request_body["detection_response"] = detection_response
        url = "%s?session_id=%s&application_id=%s&locale=%s" % (
            CONTEXT_URL, session_id, application_id, locale
        )
            if user_id is not None:
                url += "&user_id=%s" % user_id
            if skip_mongodb_log:
                url += "&skip_mongodb_log"
            http_client = HTTPClient()
            response = http_client.fetch(
                HTTPRequest(
                    url=url,
                    body=json_encode(request_body),
                    method="POST"
                )
            )
            http_client.close()
            return json_decode(response.body)
