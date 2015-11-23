from api.logic.sender import Sender as SenderLogic


class ContextResponder:

    def __init__(self, sender: SenderLogic):
        self.sender = sender

    def unsupported_entities(self, handler, context):
        if "unsupported_entities" in context and any(context["unsupported_entities"]):
            self.sender.write_jemboo_response_message(
                handler,
                {
                    "display_text": "I am sorry, I only have women's shoes"
                }
            )
