from api.handlers.ask import Ask
from api.handlers.chat import Chat
from api.handlers.feedback import Feedback
from api.handlers.proxy import Proxy

__author__ = 'robdefeo'
import tornado
import tornado.web
import tornado.options
from tornado.web import url
from api.handlers.status import Status
from api.logic.ask import Ask as AskLogic


class Application(tornado.web.Application):
    def __init__(self):
        from api.content import Content
        product_cache = Content(4096)
        ask_logic = AskLogic(product_cache)
        handlers = [
            url(r"/ask", Ask, dict(logic=ask_logic), name="ask"),
            url(r"/chat", Chat, dict(logic=ask_logic), name="chat"),
            url(r"/feedback", Feedback, name="feedback"),
            url(r"/proxy.html", Proxy, name="proxy"),
            url(r"/status", Status, name="status")
            # url(r"/refresh", Refresh, name="refresh")
        ]

        settings = dict(
            # static_path = os.path.join(os.path.dirname(__file__), "static"),
            # template_path = os.path.join(os.path.dirname(__file__), "templates"),
            debug=tornado.options.options.debug,
        )
        tornado.web.Application.__init__(self, handlers, **settings)