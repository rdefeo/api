from tornado.httpserver import HTTPServer
import tornado
import tornado.options
from tornado.ioloop import IOLoop
from api.application import Application

__author__ = 'robdefeo'

from api.settings import PORT, ADD_DEV_SSL
tornado.options.define('port', type=int, default=PORT, help='server port number (default: 9999)')
tornado.options.define('debug', type=bool, default=False, help='run in debug mode with autoreload (default: False)')


if __name__ == "__main__":
    tornado.options.parse_command_line()
    # http_server = HTTPServer(Application())
    ssl_options = None
    if ADD_DEV_SSL:
        ssl_options = {
            "certfile": "/Users/robdefeo/development/api/dev_cert/58327134-jemboo.com.cert",
            "keyfile": "/Users/robdefeo/development/api/dev_cert/58327134-jemboo.com.key",
        }

    http_server = tornado.httpserver.HTTPServer(Application(), ssl_options=ssl_options)
    http_server.listen(tornado.options.options.port)
    IOLoop.instance().start()