__author__ = 'robdefeo'


class MessageResponse:
    def detection_response(self, unknown_entities: list) -> dict:
        if any(unknown_entities):
            non_understood_entities_text = ""
            for index, x in enumerate(unknown_entities):
                if len(unknown_entities) == 1:
                    non_understood_entities_text = x["key"]
                else:
                    if index < len(unknown_entities) - 1:
                        non_understood_entities_text += "%s, "
                    else:
                        non_understood_entities_text += "and %s"

            return {
                "display_text": "I am sorry, I did not understand %s." % non_understood_entities_text
            }
        else:
            # TODO do we bother to say its all ok?
            return None

    def no_search_query_given(self):
        return {
            "display_text": "Here are the most popular and new additions."
        }
