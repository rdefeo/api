__author__ = 'robdefeo'
import random

class MessageResponse:
    def unknown_entities_detection_response(self, unknown_entities: list) -> dict:
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

            return {
                "display_text": "I am sorry, I did not understand %s." % non_understood_entities_text
            }
        else:
            # TODO do we bother to say its all ok?
            return None

    def understood_all_entities_detection_response(self, understood_entities: list) -> dict:
        templates = [
            "Ok, I found items matching %s.",
            "This is what I found for %s."
            "These should match %s."
            "For %s I found all these for you."
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

            return {
                "display_text": random.choice(templates) % understood_entities_text
            }
        else:
            return None


    def no_search_query_given(self):
        return {
            "display_text": "Here are the most popular and new additions."
        }
