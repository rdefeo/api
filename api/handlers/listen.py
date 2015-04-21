from tornado import gen
from tornado.web import RequestHandler, asynchronous


class Listen(RequestHandler):
    def initialize(self):
        pass

    def on_finish(self):
        pass

    @asynchronous
    @gen.engine
    def get(self):
        pass