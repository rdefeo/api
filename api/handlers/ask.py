__author__ = 'robdefeo'

from tornado import gen
import tornado
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPClient
from tornado.web import RequestHandler, asynchronous
from tornado.escape import json_encode, json_decode, url_escape
from api.settings import DETECT_URL, SUGGEST_URL, CONTEXT_URL


class Ask(RequestHandler):
    def initialize(self):
        pass

    def on_finish(self):
        pass

    def get_context(self, session_id, user_id, context_id):
        http_client = HTTPClient()
        if context_id is None:
            context_response = http_client.fetch(
                HTTPRequest(
                    url="%s?user_id=%s&session_id=%s" % (CONTEXT_URL, user_id, session_id),
                    body=json_encode({}),
                    method="POST"
                )
            )
            return json_decode(context_response.body)
        else:
            context_response = http_client.fetch(
                HTTPRequest(
                    url="%s/%s?user_id=%s&session_id=%s" % (CONTEXT_URL, context_id, user_id, session_id),
                    method="GET"
                )
            )
            return json_decode(context_response.body)

    @asynchronous
    @gen.engine
    def get(self):
        self.set_header('Content-Type', 'application/json')

        user_id = self.get_argument("user_id", None)
        context_id = self.get_argument("context_id", None)
        session_id = self.get_argument("session_id", None)
        locale = self.get_argument("locale", None)
        query = self.get_argument("q", None)
        page = int(self.get_argument("page", 1))
        page_size = int(self.get_argument("page_size", 10))

        if user_id is None:
            self.set_status(412)
            self.finish(
                {
                    "status": "error",
                    "message": "missing param=user_id"
                }
            )
        elif context_id is not None and query is not None:
            self.set_status(412)
            self.finish(
                {
                    "status": "error",
                    "message": "can not combine params=[q,context_id]"
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
            detection_response = None
            if query is not None:
                raise NotImplemented()

            context = self.get_context(session_id, user_id, context_id)
            http_client = HTTPClient()
            suggest_response = http_client.fetch(
                HTTPRequest(
                    url="%s?user_id=%s&session_id=%s&locale=%s&page=%s&page_size=%s&context=%s" % (
                        SUGGEST_URL,
                        user_id,
                        session_id,
                        locale,
                        page,
                        page_size,
                        url_escape(json_encode(context))
                    )
                )
            )
            links = [
                self.build_header_link(
                    self.build_link(
                        session_id,
                        user_id,
                        context["_id"],
                        locale,
                        page + 1,
                        page_size
                    ),
                    "next"
                )
            ]
            self.set_header(
                "Link",
                ", ".join(links)
            )
            self.finish(
                {
                    "suggestions": json_decode(suggest_response.body)["suggestions"]
                }
            )
            pass

    def build_header_link(self, href, rel):
        return "<%s>; rel=\"%s\"" % (href, rel)

    def build_link(self, session_id, user_id, context_id, locale, new_page, page_size):
        return "http://%s%s?session_id=%s&user_id=%s&context_id=%s&locale=%s&page=%s&page_size=%s" % (
            self.request.host,
            self.request.path,
            session_id,
            user_id,
            context_id,
            locale,
            new_page,
            page_size
        )
