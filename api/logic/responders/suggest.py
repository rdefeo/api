from api.logic.sender import Sender as SenderLogic


class SuggestResponder:
    def __init__(self, sender: SenderLogic):
        self.sender = sender

    def suggestion_items(self, handler, message: dict, suggestion_items: list):
        if message["offset"] == 0:
            # TODO first page so probably say here about how many we found for the search query
            pass
            return

        if message["offset"] == 40:
            # its a couple of pages in so nows a good time to ask a follow up question probably generic for now
            self.sender.write_jemboo_response_message(
                handler,
                {
                    "display_text": "Is there anything else you would like me to find for you?"
                }
            )
            return

        return
