from collections import defaultdict

import tornado
import tornado.web
import tornado.options
from tornado.web import url

from api.handlers.ask import Ask
from api.handlers.chat import Chat
from api.handlers.feedback import Feedback
from api.handlers.proxy import Proxy
from api.handlers.status import Status
from api.handlers.cache import Cache
from api.handlers.websocket import WebSocket
from api.logic.ask import Ask as AskLogic
from api.handlers import FacebookUserHandler
client_handlers = defaultdict(dict)


class Application(tornado.web.Application):
    def __init__(self):
        from api.cache import ProductDetailCache
        product_cache = ProductDetailCache(4096)
        ask_logic = AskLogic(product_cache)
        # ws_logic = WebSocketLogic(product_cache)

        handlers = [
            # /ws/product -> Push notifications etc
            # /ws/ask
            # /ws/ask -> Msg -> Conversation

            # /ws/context
            # /rs/context
            # /rs/context/messages
            url(
                r"/websocket",
                WebSocket, dict(
                    product_content=product_cache,
                    client_handlers=client_handlers
                ),
                name="websocket"),
            url(r"/ask", Ask, dict(logic=ask_logic), name="ask"),
            url(r"/cache", Cache, dict(product_cache=product_cache), name="cache"),
            url(r"/chat", Chat, dict(logic=ask_logic), name="chat"),
            url(r"/feedback", Feedback, name="feedback"),
            url(r"/proxy.html", Proxy, name="proxy"),
            url(r"/status", Status, name="status"),
            # USER SERVICE
            url(r"/user/facebook", FacebookUserHandler, name="facebook_user")
                # url(r"/refresh", Refresh, name="refresh")
        ]

        settings = dict(
            # static_path = os.path.join(os.path.dirname(__file__), "static"),
            # template_path = os.path.join(os.path.dirname(__file__), "templates"),
            debug=tornado.options.options.debug,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
