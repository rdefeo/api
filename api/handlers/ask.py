from api.settings import ADD_CORS_HEADERS

__author__ = 'robdefeo'

from tornado import gen
from tornado.web import RequestHandler, asynchronous


class Ask(RequestHandler):
    def initialize(self, logic):
        self.logic = logic

    def set_default_headers(self):
        if ADD_CORS_HEADERS:
            self.set_header("Access-Control-Allow-Origin", "*")

    def on_finish(self):
        pass

    @asynchronous
    @gen.engine
    def get(self):
        self.set_header('Content-Type', 'application/json')

        user_id = self.get_argument("user_id", None)
        application_id = self.get_argument("application_id", None)
        context_id = self.get_argument("context_id", None)
        session_id = self.get_argument("session_id", None)
        locale = self.get_argument("locale", None)
        query = self.get_argument("q", None)
        offset = int(self.get_argument("offset", 0))
        page_size = int(self.get_argument("page_size", 10))

        if application_id is None:
            self.set_status(412)
            self.finish(
                {
                    "status": "error",
                    "message": "missing param=application_id"
                }
            )
        elif session_id is None:
            self.set_status(412)
            self.finish(
                {
                    "status": "error",
                    "message": "missing param=session_id"
                }
            )
        elif locale is None:
            self.set_status(412)
            self.finish(
                {
                    "status": "error",
                    "message": "missing param=locale"
                }
            )
        else:
            skip_mongodb_log = self.get_argument("skip_mongodb_log", None) is not None
            response = self.logic.do(user_id, application_id, session_id, context_id, query, locale, offset, page_size, skip_mongodb_log)
            self.set_status(200)
            self.set_header(
                "Link",
                ", ".join(
                    self.logic.build_header_links(
                        self.request.host,
                        self.request.path,
                        user_id,
                        application_id,
                        session_id,
                        response["context_id"],
                        locale,
                        offset,
                        page_size
                    )
                )
            )
            self.finish(response)
            pass
