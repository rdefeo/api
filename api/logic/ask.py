from tornado.escape import url_escape, json_decode, json_encode
from tornado.httpclient import HTTPRequest, HTTPClient
from api.logic.generic import Generic
from api.settings import DETECT_URL, SUGGEST_URL, CONTEXT_URL
from tornado.log import app_log


class Ask(Generic):
    def __init__(self, content):
        self.content = content

    @staticmethod
    def get_wit_detection(user_id, application_id, session_id, locale, query, context):
        url="%s/wit?application_id=%s&session_id=%s&locale=%s&q=%s" % (
            DETECT_URL,
            application_id,
            session_id,
            locale,
            url_escape(query)
            # url_escape(json_encode(context))
        )
        if user_id is not None:
            url += "&user_id=%s" % user_id
        http_client = HTTPClient()
        response = http_client.fetch(
            HTTPRequest(url=url)
        )
        http_client.close()
        return json_decode(response.body)

    def get_detection_context(self, user_id, application_id, session_id, context_id, locale, query, skip_mongodb_log):
        context = self.get_context(user_id, application_id, session_id, locale, None, context_id, skip_mongodb_log)
        if query is not None:
            detection_response = self.get_wit_detection(user_id, application_id, session_id, locale, query, context)
            # now don't pass the context_id cus for sure it will be replaced by the new detection
            context = self.get_context(user_id, application_id, session_id, locale, detection_response, context_id, skip_mongodb_log)
            return context, detection_response
        else:
            return context, None

    def get_context(self, user_id, application_id, session_id, locale, detection_response, context_id, skip_mongodb_log):
        if context_id is None or detection_response is not None:
            request_body = {}
            if detection_response is not None:
                request_body["detection_response"] = detection_response
            url = "%s?session_id=%s&application_id=%s&locale=%s" % (
                CONTEXT_URL, session_id, application_id, locale
            )
            if user_id is not None:
                url += "&user_id=%s" % user_id
            if skip_mongodb_log:
                url += "&skip_mongodb_log"
            http_client = HTTPClient()
            response = http_client.fetch(
                HTTPRequest(
                    url=url,
                    body=json_encode(request_body),
                    method="POST"
                )
            )
            http_client.close()
            return json_decode(response.body)
        else:
            http_client = HTTPClient()
            url = "%s?context_id=%s&session_id=%s" % (CONTEXT_URL, context_id, session_id)
            if user_id is not None:
                url += "&user_id=%s" % user_id

            context_response = http_client.fetch(
                HTTPRequest(
                    url=url,
                    method="GET"
                )
            )
            http_client.close()
            return json_decode(context_response.body)

    def do(self, user_id, application_id, session_id, context_id, query, locale, offset, page_size, skip_mongodb_log):
        context, detection_response = self.get_detection_context(
            user_id, application_id, session_id, context_id, locale, query, skip_mongodb_log
        )

        suggest_response = self.get_suggestion(user_id, application_id, session_id, locale, offset, page_size, context, skip_mongodb_log)
        suggestions = self.fill_suggestions(suggest_response["suggestions"])

        response = {
            "suggestions": suggestions,
            "offset": offset,
            "page_size": page_size,
            "context_id": context["_id"]
        }

        if detection_response is not None:
            if "non_detections" in detection_response and any(detection_response["non_detections"]):
                response["non_detections"] = detection_response["non_detections"]

            if "autocorrected" in detection_response:
                response["autocorrected"] = detection_response["autocorrected"]

        return response

    def get_tile(self, suggestion):
        for image in suggestion["images"]:
            if "tiles" in image:
                for tile in image["tiles"]:
                    if tile["w"] == "w-md":
                        return {
                            "colspan": 1,
                            "rowspan": 1 if tile["h"] == "h-md" else 2,
                            "image_url": tile["path"]
                        }

    def fill_suggestions(self, suggestions):
        items = []
        for suggestion in suggestions:
            new_suggestion = self.content.product_cache(suggestion["_id"])
            if new_suggestion is not None:
                new_suggestion["tile"] = self.get_tile(new_suggestion)
                new_suggestion["score"] = suggestion["score"]
                new_suggestion["reasons"] = suggestion["reasons"]
                new_suggestion["_id"] = suggestion["_id"]
                items.append(new_suggestion)
        return items

    def build_header_link(self, href, rel):
        return "<%s>; rel=\"%s\"" % (href, rel)

    def build_header_links(self, host, path, user_id, application_id, session_id, context_id, locale, offset, page_size):
        links = [
            self.build_header_link(
                self.build_link(
                    host, path,
                    application_id,
                    session_id,
                    user_id,
                    context_id,
                    locale,
                    offset + page_size,
                    page_size
                ),
                "next"
            )
        ]
        if offset > 1:
            links.append(
                self.build_header_link(
                    self.build_link(
                        host, path,
                        application_id,
                        session_id,
                        user_id,
                        context_id,
                        locale,
                        offset - page_size,
                        page_size
                    ),
                    "prev"
                )
            )
            links.append(
                self.build_header_link(
                    self.build_link(
                        host, path,
                        application_id,
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

    def build_link(self, host, path, user_id, application_id, session_id,  context_id, locale, offset, page_size):
        return "http://%s%s?application_id=%s&session_id=%s&user_id=%s&context_id=%s&locale=%s&offset=%s&page_size=%s" % (
            host,
            path,
            application_id,
            session_id,
            user_id,
            context_id,
            locale,
            offset,
            page_size
        )

    def get_suggestion(self, user_id, application_id, session_id, locale, offset, page_size, context, skip_mongodb_log):
        url = "%s?application_id=%s&session_id=%s&locale=%s&offset=%s&page_size=%s&context=%s" % (
            SUGGEST_URL,
            application_id,
            session_id,
            locale,
            offset,
            page_size,
            url_escape(json_encode(context))
        )
        if user_id is not None:
                url += "&user_id=%s" % user_id
        if skip_mongodb_log:
            url += "&skip_mongodb_log"

        app_log.debug("get_suggestions,url=%s",url)
        http_client = HTTPClient()
        suggest_response = http_client.fetch(
            HTTPRequest(
                url=url
            )
        )
        http_client.close()
        return json_decode(suggest_response.body)

    def get_detection(self, user_id, application_id, session_id, locale, query, context):
        url="%s?application_id=%s&session_id=%s&locale=%s&q=%s" % (
            DETECT_URL,
            application_id,
            session_id,
            locale,
            url_escape(query)
            # url_escape(json_encode(context))
        )
        if user_id is not None:
            url += "&user_id=%s" % user_id
        http_client = HTTPClient()
        response = http_client.fetch(
            HTTPRequest(url=url)
        )
        http_client.close()
        return json_decode(response.body)