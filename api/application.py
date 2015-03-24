from api.handlers.ask import Ask

__author__ = 'robdefeo'
import tornado
import tornado.web
import tornado.options
from tornado.web import url
from api.handlers.status import Status


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            url(r"/ask", Ask, name="ask"),
            # url(r"/proxy.html", Proxy, name="proxy"),
            url(r"/status", Status, name="status")
            # url(r"/refresh", Refresh, name="refresh")
        ]

        settings = dict(
            # static_path = os.path.join(os.path.dirname(__file__), "static"),
            # template_path = os.path.join(os.path.dirname(__file__), "templates"),
            debug=tornado.options.options.debug,
        )
        tornado.web.Application.__init__(self, handlers, **settings)