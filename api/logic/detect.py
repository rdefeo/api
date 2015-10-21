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

    def understood_entities(self, outcomes: list) -> list:
        for outcome in outcomes:
            for entity in outcome["entities"]:
                if entity["confidence"] > 40.0:
                    yield entity

    def respond_to_detection_response(self, handler: WebSocketHandler, detection_response: dict):
        # TODO 25 non detected items
        unknown_entities = list(self.unknown_entities(detection_response["outcomes"]))
        unknown_entities_response = self.message_response.detection_response(unknown_entities)
        if unknown_entities_response is not None:
            self.write_jemboo_response_message(handler_callback, detection_chat_response)


        # for outcome in detection_response["outcomes"]:
        #     # then check concept
        #     if outcome["confidence"] < 50.0:
        #         # its got no idea
        #         break
        # pass
