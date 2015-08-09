from tornado.escape import json_decode, json_encode, url_escape
from tornado.httpclient import HTTPClient, HTTPRequest
from api.settings import CONTEXT_URL, DETECT_URL

__author__ = 'robdefeo'


class Generic:
    pass
    # @staticmethod
    # def get_wit_detection(user_id, application_id, session_id, locale, query, context):
    #     url="%s/wit?application_id=%s&session_id=%s&locale=%s&q=%s" % (
    #         DETECT_URL,
    #         application_id,
    #         session_id,
    #         locale,
    #         url_escape(query)
    #         # url_escape(json_encode(context))
    #     )
    #     if user_id is not None:
    #         url += "&user_id=%s" % user_id
    #     http_client = HTTPClient()
    #     response = http_client.fetch(
    #         HTTPRequest(url=url)
    #     )
    #     http_client.close()
    #     return json_decode(response.body)
    #
    # def get_detection_context(self, user_id, application_id, session_id, context_id, locale, query, skip_mongodb_log):
    #     context = self.get_context(user_id, application_id, session_id, locale, None, context_id, skip_mongodb_log)
    #     if query is not None:
    #         detection_response = self.get_wit_detection(user_id, application_id, session_id, locale, query, context)
    #         # now don't pass the context_id cus for sure it will be replaced by the new detection
    #         context = self.get_context(user_id, application_id, session_id, locale, detection_response, context_id, skip_mongodb_log)
    #         return context, detection_response
    #     else:
    #         return context, None
    #
    # def get_context(self, user_id, application_id, session_id, locale, detection_response, context_id, skip_mongodb_log):
    #     if context_id is None or detection_response is not None:
    #         request_body = {}
    #         if detection_response is not None:
    #             request_body["detection_response"] = detection_response
    #         url = "%s?session_id=%s&application_id=%s&locale=%s" % (
    #             CONTEXT_URL, session_id, application_id, locale
    #         )
    #         if user_id is not None:
    #             url += "&user_id=%s" % user_id
    #         if skip_mongodb_log:
    #             url += "&skip_mongodb_log"
    #         http_client = HTTPClient()
    #         response = http_client.fetch(
    #             HTTPRequest(
    #                 url=url,
    #                 body=json_encode(request_body),
    #                 method="POST"
    #             )
    #         )
    #         http_client.close()
    #         return json_decode(response.body)
    #     else:
    #         http_client = HTTPClient()
    #         url = "%s?context_id=%s&session_id=%s" % (CONTEXT_URL, context_id, session_id)
    #         if user_id is not None:
    #             url += "&user_id=%s" % user_id
    #
    #         context_response = http_client.fetch(
    #             HTTPRequest(
    #                 url=url,
    #                 method="GET"
    #             )
    #         )
    #         http_client.close()
    #         return json_decode(context_response.body)