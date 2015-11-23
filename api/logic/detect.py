import logging

from tornado.escape import url_escape, json_encode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError

from api.handlers.websocket import WebSocket as WebSocketHandler
from api.logic.responders import DetectResponder
from api.logic.sender import Sender
from api.settings import DETECT_URL, LOGGING_LEVEL


class Detect:
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    def __init__(self, sender: Sender):
        self.responder = DetectResponder(sender)
        self.sender = sender

    def get_detect(self, location: str, callback) -> dict:
        self.logger.debug("location=%s", location)
        url = "%s%s" % (DETECT_URL, location)
        try:
            http_client = AsyncHTTPClient()
            http_client.fetch(HTTPRequest(url=url, method="GET"), callback=callback)
            http_client.close()
        except HTTPError as e:
            self.logger.error("get_detect,url=%s", url)
            raise

    def post_detect(self, user_id: str, application_id: str, session_id: str, locale: str, query: str, callback) -> str:
        self.logger.debug(
            "user_id=%s,application_id=%s,session_id=%s,locale=%s,query=%s",
            user_id, application_id, session_id, locale, query
        )

        url = "%s?application_id=%s&session_id=%s&locale=%s&q=%s" % (
            DETECT_URL,
            application_id,
            session_id,
            locale,
            url_escape(query)
            # url_escape(json_encode(context))
        )
        if user_id is not None:
            url += "&user_id=%s" % user_id
        http_client = AsyncHTTPClient()
        http_client.fetch(
            HTTPRequest(url=url, method="POST", body=json_encode({})),
            callback=callback
        )
        http_client.close()

    def unknown_entities(self, outcomes: list) -> list:
        for outcome in outcomes:
            for entity in outcome["entities"]:
                if entity["confidence"] < 40.0:
                    yield entity

    def understood_entities(self, outcomes: list) -> list:
        for outcome in outcomes:
            for entity in outcome["entities"]:
                if entity["confidence"] > 40.0:
                    yield entity

    def respond_to_detection_response(self, handler: WebSocketHandler, detection_response: dict):
        # TODO 25 non detected items
        unknown_entities = list(self.unknown_entities(detection_response["outcomes"]))
        unknown_entities_response = self.responder.unknown_entities_detection_response(handler, unknown_entities)
        if unknown_entities_response is None:
            self.responder.understood_all_entities_detection_response(
                handler,
                list(self.understood_entities(detection_response["outcomes"]))
            )
