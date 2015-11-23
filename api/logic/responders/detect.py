import random

from api.logic.sender import Sender as SenderLogic


class DetectResponder:
    def __init__(self, sender: SenderLogic):
        self.sender = sender

    def unknown_entities_detection_response(self, handler, unknown_entities: list) -> dict:
        if any(unknown_entities):
            non_understood_entities_text = ""
            for index, x in enumerate(unknown_entities):
                if len(unknown_entities) == 1:
                    non_understood_entities_text = x["key"]
                else:
                    if index < len(unknown_entities) - 1:
                        non_understood_entities_text += "%s, " % x["key"]
                    else:
                        non_understood_entities_text += "and %s" % x["key"]

            message = {
                "display_text": "I am sorry, I did not understand %s." % non_understood_entities_text
            }
            self.sender.write_jemboo_response_message(
                handler,
                message
            )
            return message
        else:
            return None

    def understood_all_entities_detection_response(self, handler, understood_entities: list) -> dict:
        templates = [
            "Ok, I found items matching {0}.",
            "This is what I found for {0}.",
            "These should match {0}.",
            "For {0} I found all these for you."
        ]
        if any(understood_entities):
            understood_entities_text = ""
            for index, x in enumerate(understood_entities):
                if len(understood_entities) == 1:
                    understood_entities_text = x["key"]
                else:
                    if index < len(understood_entities) - 1:
                        understood_entities_text += "%s, " % x["key"]
                    else:
                        understood_entities_text += "and %s" % x["key"]

            # TODO obviously needs dealing with in a much better way

            # self.sender.write_jemboo_response_message(
            #     handler,
            #     {
            #         "display_text": random.choice(templates).format(understood_entities_text)
            #     }
            # )
        else:
            return None

    def no_search_query_given(self):
        return {
            "display_text": "Here are the most popular and new additions."
        }
