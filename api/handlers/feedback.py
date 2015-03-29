from tornado.escape import url_escape, json_decode, json_encode
from tornado.httpclient import HTTPRequest, HTTPClient, AsyncHTTPClient
from api.settings import CONTEXT_URL

__author__ = 'robdefeo'

from tornado import gen
from tornado.web import RequestHandler, asynchronous


class Feedback(RequestHandler):
    def initialize(self):
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')

    def on_finish(self):

        pass

    def options(self, *args, **kwargs):
        self.finish()

    @asynchronous
    @gen.engine
    def post(self, *args, **kwargs):
        self.set_header('Content-Type', 'application/json')
        user_id = self.get_argument("user_id", None)
        session_id = self.get_argument("session_id", None)
        context_id = self.get_argument("context_id", None)
        application_id = self.get_argument("application_id", None)
        product_id = self.get_argument("product_id", None)
        _type = self.get_argument("type", None)
        body = json_decode(self.request.body)

        if application_id is None:
            self.set_status(412)
            self.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing param=application_id"
                    }
                )
            )
        elif session_id is None:
            self.set_status(412)
            self.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing param=session_id"
                    }
                )
            )
        elif product_id is None:
            self.set_status(412)
            self.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing param=product_id"
                    }
                )
            )
        else:
            url = "%s/feedback?session_id=%s&application_id=%s&product_id=%s&type=%s" % (
                CONTEXT_URL,
                session_id,
                application_id,
                product_id,
                _type
            )

            if user_id is not None:
                url += "&user_id=%s" % user_id
            if context_id is not None:
                url += "&context_id=%s" % context_id
            # http_client = HTTPClient()
            #
            # response = http_client.fetch(
            #     HTTPRequest(
            #         url=url,
            #         body=json_encode(body),
            #         method="POST"
            #     )
            # )
            #
            # http_client.close()
            # self.set_status(response.status)
            # self.finish(response.body)
            http_client = AsyncHTTPClient()
            http_client.fetch(
                HTTPRequest(
                    url=url,
                    body=json_encode(body),
                    method="POST"
                ),
                self.context_feedback_response_handler
            )
            http_client.close()

    def context_feedback_response_handler(self, response):
        self.set_status(response.code)
        self.finish(response.body)

