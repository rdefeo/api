from api.handlers.websocket import WebSocket as WebSocketHandler
from api.logic.incoming_message_handlers.message_handler import MessageHandler
from api.logic.responders.suggest import SuggestResponder
from api.logic import SenderLogic


class NextPage(MessageHandler):
    def __init__(self, suggestions, sender: SenderLogic):
        self.suggestions = suggestions
        self.suggest_responder = SuggestResponder(sender)

    def on_next_page_message(self, handler: WebSocketHandler, message: dict):
        self.suggestions.get_suggestion_items(
            handler.user_id,
            handler.application_id,
            handler.session_id,
            handler.locale,
            message["suggest_id"],
            handler.page_size,
            message["offset"],
            callback=lambda res: self.get_suggestion_items_callback(res, handler, message)
        )

    def get_suggestion_items_callback(self, response, handler: WebSocketHandler, message: dict):
        suggestion_items_response = self.bson_json_decode_and_load(response.body)
        next_offset = response.headers["next_offset"]
        self.suggest_responder.suggestion_items(handler, message, suggestion_items_response)
        self.suggestions.write_suggestion_items(handler, suggestion_items_response, message["offset"], next_offset)
