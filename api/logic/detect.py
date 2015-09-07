from api.handlers.websocket import WebSocket as WebSocketHandler
from api.logic.message_response import MessageResponse


class Detect:

    def __init__(self):
        self.message_response = MessageResponse()
    def unknown_entities(self, outcomes: list) -> list:
        for outcome in outcomes:
            for entity in outcome["entities"]:
                if entity["confidence"] < 40.0:
                    yield entity

    def respond_to_detection_response(self, handler: WebSocketHandler, detection_response: dict):
        # TODO 25 non detected items
        return self.message_response.detection_response(
            list(self.unknown_entities(detection_response["outcomes"]))
        )

        # for outcome in detection_response["outcomes"]:
        #     # then check concept
        #     if outcome["confidence"] < 50.0:
        #         # its got no idea
        #         break
        # pass
