__author__ = 'robdefeo'

from tornado import gen
import tornado
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPClient
from tornado.web import RequestHandler, asynchronous
from tornado.escape import json_encode, json_decode, url_escape
from api.settings import DETECT_URL, SUGGEST_URL, CONTEXT_URL


class Ask(RequestHandler):
    def initialize(self, content):
        self.content = content

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def on_finish(self):
        pass

    def get_context(self, session_id, user_id, detection_response, context_id):
        http_client = HTTPClient()
        if context_id is None or detection_response is not None:
            request_body = {}
            if detection_response is not None:
                request_body["detection_response"] = detection_response

            response = http_client.fetch(
                HTTPRequest(
                    url="%s?user_id=%s&session_id=%s" % (CONTEXT_URL, user_id, session_id),
                    body=json_encode(request_body),
                    method="POST"
                )
            )
            return json_decode(response.body)
        else:
            context_response = http_client.fetch(
                HTTPRequest(
                    url="%s/%s?user_id=%s&session_id=%s" % (CONTEXT_URL, context_id, user_id, session_id),
                    method="GET"
                )
            )
            return json_decode(context_response.body)

    def get_suggestion(self, user_id, session_id, locale, page, page_size, context):
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
        return json_decode(suggest_response.body)

    def get_detection(self, user_id, session_id, locale, query, context):
        http_client = HTTPClient()
        response = http_client.fetch(
            HTTPRequest(
                url="%s?user_id=%s&session_id=%s&locale=%s&q=%s" % (
                    DETECT_URL,
                    user_id,
                    session_id,
                    locale,
                    url_escape(query)
                    # url_escape(json_encode(context))
                )

            )
        )
        return json_decode(response.body)

    @asynchronous
    @gen.engine
    def get(self):
        self.set_header('Content-Type', 'application/json')

        user_id = self.get_argument("user_id", "None")
        context_id = self.get_argument("context_id", None)
        session_id = self.get_argument("session_id", None)
        locale = self.get_argument("locale", None)
        query = self.get_argument("q", None)
        page = int(self.get_argument("page", 1))
        page_size = int(self.get_argument("page_size", 10))

        if session_id is None:
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
            context = self.get_context(session_id, user_id, None, context_id)
            if query is not None:
                detection_response = self.get_detection(user_id, session_id, locale, query, context)
                # now don't pass the context_id cus for sure it will be replaced by the new detection
                context = self.get_context(session_id, user_id, detection_response, context_id)

            suggest_response = self.get_suggestion(user_id, session_id, locale, page, page_size, context)
            suggestions = list(self.fill_suggestions(suggest_response["suggestions"]))

            self.set_status(200)
            self.set_header(
                "Link",
                ", ".join(
                    self.build_header_links(
                        session_id,
                        user_id,
                        context["_id"],
                        locale,
                        page,
                        page_size
                    )
                )
            )
            self.finish(
                {
                    "suggestions": suggestions,
                    "page": page,
                    "page_size": page_size,
                    "context_id": context_id
                }
            )
            pass

    def fill_suggestions(self, suggestions):
        for x in suggestions:
            y = self.content.product_cache(x["_id"])
            y["score"] = x["score"]
            y["_id"] = x["_id"]
            yield y

    def build_header_links(self, session_id, user_id, context_id, locale, page, page_size):
        links = [
                self.build_header_link(
                    self.build_link(
                        session_id,
                        user_id,
                        context_id,
                        locale,
                        page + 1,
                        page_size
                    ),
                    "next"
                )
            ]
        if page > 1:
            links.append(
                self.build_header_link(
                    self.build_link(
                        session_id,
                        user_id,
                        context_id,
                        locale,
                        page - 1,
                        page_size
                    ),
                    "prev"
                )
            )
            links.append(
                self.build_header_link(
                    self.build_link(
                        session_id,
                        user_id,
                        context_id,
                        locale,
                        1,
                        page_size
                    ),
                    "first"
                )
            )
        return links

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
