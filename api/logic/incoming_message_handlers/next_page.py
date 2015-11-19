from api.handlers.websocket import WebSocket as WebSocketHandler
from bson.json_util import dumps, loads


class NextPage:
    def __init__(self, suggestions):
        self.suggestions = suggestions

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
        suggestion_items_response = loads(response.body.decode("utf-8"))
        next_offset = response.headers["next_offset"]
        self.suggestions.write_suggestion_items(handler, suggestion_items_response, message["offset"], next_offset)
