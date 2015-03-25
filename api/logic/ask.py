from tornado.escape import url_escape, json_decode, json_encode
from tornado.httpclient import HTTPRequest, HTTPClient
from api.settings import DETECT_URL, SUGGEST_URL, CONTEXT_URL

__author__ = 'robdefeo'


class Ask(object):
    def __init__(self, content):
        self.content = content

    def get_detection_context(self, context_id, locale, query, session_id, user_id):
        context = self.get_context(session_id, user_id, None, context_id)
        if query is not None:
            detection_response = self.get_detection(user_id, session_id, locale, query, context)
            # now don't pass the context_id cus for sure it will be replaced by the new detection
            context = self.get_context(session_id, user_id, detection_response, context_id)
            return context, detection_response
        else:
            return context, None

    def do(self, user_id, session_id, context_id, query, locale, page, page_size):
        context, detection_response = self.get_detection_context(context_id, locale, query, session_id, user_id)

        suggest_response = self.get_suggestion(user_id, session_id, locale, page, page_size, context)
        suggestions = list(self.fill_suggestions(suggest_response["suggestions"]))

        response = {
            "suggestions": suggestions,
            "page": page,
            "page_size": page_size,
            "context_id": context["_id"]
        }

        if detection_response is not None and "non_detections" in detection_response and any(detection_response["non_detections"]):
            response["non_detections"] = detection_response["non_detections"]

        return response

    def fill_suggestions(self, suggestions):
        for x in suggestions:
            y = self.content.product_cache(x["_id"])
            y["score"] = x["score"]
            y["_id"] = x["_id"]
            yield y

    def build_header_link(self, href, rel):
        return "<%s>; rel=\"%s\"" % (href, rel)

    def build_header_links(self, host, path, session_id, user_id, context_id, locale, page, page_size):
        links = [
            self.build_header_link(
                self.build_link(
                    host, path,
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
                        host, path,
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
                        host, path,
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

    def build_link(self, host, path, session_id, user_id, context_id, locale, new_page, page_size):
        return "http://%s%s?session_id=%s&user_id=%s&context_id=%s&locale=%s&page=%s&page_size=%s" % (
            host,
            path,
            session_id,
            user_id,
            context_id,
            locale,
            new_page,
            page_size
        )

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