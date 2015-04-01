from tornado import gen
import tornado
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, asynchronous
from tornado.escape import json_encode
from api.settings import DETECT_URL, SUGGEST_URL, CONTEXT_URL
from api import __version__


class Status(RequestHandler):
    def initialize(self):
        pass

    def on_finish(self):
        pass

    @asynchronous
    @gen.engine
    def get(self):
        http_client = AsyncHTTPClient()
        detect_response, suggest_response, context_response = yield [
            gen.Task(
                http_client.fetch,
                "%s/status" % DETECT_URL
            ),
            gen.Task(
                http_client.fetch,
                "%s/status" % SUGGEST_URL
            ),
            gen.Task(
                http_client.fetch,
                "%s/status" % CONTEXT_URL
            )
        ]
        services = [
            self.check_service_status(detect_response, "detect"),
            self.check_service_status(suggest_response, "suggest"),
            self.check_service_status(context_response, "context")
        ]
        self.set_header('Content-Type', 'application/json')
        self.set_status(200)
        self.finish({
            "services": services,
            "status": "OK" if not any(x for x in services if x["status"] != "OK") else "NOT_OK",
            "version": __version__
        })

    def check_service_status(self, response, name):
        if response.reason == "OK":
            data = tornado.escape.json_decode(response.body)
            return {
                "key": name,
                "status": data["status"]
            }
        else:
            return {
                "key": name,
                "status": response.reason,
                "error": str(response.error)
            }