from collections import defaultdict
from tornado.escape import json_decode, json_encode
from tornado.websocket import WebSocketHandler
from bson.objectid import ObjectId
__author__ = 'robdefeo'


class Chat(WebSocketHandler):
    def initialize(self, logic):
        self.logic = logic
        self.conversations = {}

    def check_origin(self, origin):
        # TODO needs serious production ready work
        return True

    def application_id(self):
        return ObjectId(self.get_argument("application_id"))

    def session_id(self):
        return ObjectId(self.get_argument("session_id"))

    def page_size(self):
        return int(self.get_argument("page_size"))

    def conversation_id(self):
        return ObjectId(self.get_argument("conversation_id"))

    def skip_mongodb_log(self):
        return self.get_argument("skip_mongodb_log", None) is not None

    def user_id(self):
        return None

    def conversation(self):
        return self.conversations[self.conversation_id()]

    def contexts(self):
        return self.conversation()["contexts"]

    def last_context_id(self):
        contexts = self.contexts()
        if any(contexts):
            return contexts[-1]["_id"]
        else:
            return None

    def add_context(self, context):
        self.contexts().append(context)

    def provided_locale(self):
        return self.get_argument("locale")

    def open(self):
        if self.conversation_id() not in self.conversations:
            self.conversations[self.conversation_id()] = {
                "application_id": self.application_id(),
                "contexts": []

            }

        # Chat.waiters.add(self)
        self.send_message_to_client(
            {
                "type": "conversation",
                "message": "Hi, how can I help you?",
                "expect_response": True
            }

        )

    def send_message_to_client(self, message):
        self.write_message(json_encode(message))

    def on_connection_close(self):
        pass

    def on_close(self):
        pass
        # Chat.waiters.remove(self)

    def combine_contexts(self):
        contexts = self.contexts()
        entities_dict = {}
        for index, context in enumerate(contexts):
            for x in context["entities"]:
                entities_dict["%s_*_*%s" % (x["type"], x["key"])] = {
                    "key": x["key"],
                    "type": x["type"],
                    "source": x["source"],
                    "weighting": x["weighting"],
                    "weighting_ages": x["weighting"] * ((index + 1) / len(contexts))
                }

        return {
            "entities": list(entities_dict.values())
        }

    def on_message(self, message):
        data = json_decode(message)
        if data["type"] == "text":
            new_context, detection_response = self.logic.get_detection_context(
                self.user_id(),
                self.application_id(),
                self.session_id(),
                self.last_context_id(),
                self.provided_locale(),
                data["text"],
                self.skip_mongodb_log()
            )
            self.add_context(new_context)
            failed_disambiguations = [x for x in detection_response["outcomes"][0]["entities"] if not any(x["disambiguated_outcomes"])]
            successful_disambiguations = [x for x in detection_response["outcomes"][0]["entities"] if any(x["disambiguated_outcomes"])]
            if any(failed_disambiguations):
                pass
                self.send_message_to_client(
                    {
                        "type": "conversation",
                        "message": "Sorry I did not understand %s is that a %s?" % (failed_disambiguations[0]["key"], failed_disambiguations[0]["type"])
                    }

                )

            if any(successful_disambiguations):
                combined_contexts = self.combine_contexts()
                num_to_look_for_in_suggestions = 250
                suggest_response = self.logic.get_suggestion(
                    self.user_id(),
                    self.application_id(),
                    self.session_id(),
                    self.provided_locale(),
                    0,
                    num_to_look_for_in_suggestions,
                    combined_contexts,
                    True
                )

                suggestions_to_return = suggest_response["suggestions"][:self.page_size()]
                suggestions = self.logic.fill_suggestions(suggestions_to_return)
                self.send_message_to_client(
                    {
                        "type": "conversation",
                        "message": "We found these for you",
                        "expect_response": False
                    }

                )
                self.send_message_to_client(
                    {
                        "type": "suggestions",
                        "suggestions": suggestions,
                        "page_offset": 0
                    }
                )

                # get common attributes
                suggestions_to_look_for_common = self.logic.fill_suggestions(suggest_response["suggestions"])
                common_attributes = self.get_common_attributes(suggestions_to_look_for_common)
                # sorted(attribute_scores.items(), key=lambda y: y[1], reverse=True)
                suggestion_attribute_type_list = ["style", "material", "theme", "color"]
                already_covered_attribute_types = list(set([x["type"] for x in combined_contexts["entities"] if x["source"] == "detection"]))

                attribute_types_to_look_for = [x for x in suggestion_attribute_type_list if x not in already_covered_attribute_types]
                top_attributes_to_suggest = [x for x in common_attributes if x["type"] in attribute_types_to_look_for and x["count"] < num_to_look_for_in_suggestions]
                ones_to_actually_return = [x for x in top_attributes_to_suggest if x["type"] == top_attributes_to_suggest[0]["type"]]
                if len(ones_to_actually_return) > 3:
                    self.send_message_to_client(
                        {
                            "type": "conversation",
                            "message": "How about %s, %s or %s" % (ones_to_actually_return[0]["key"], ones_to_actually_return[1]["key"], ones_to_actually_return[2]["key"]),
                            "expect_response": True
                        }

                    )
                pass

        elif data["type"] == "more":
            pass
        else:
            raise NotImplementedError(data["type"])

        pass

    def get_common_attributes(self, suggestions):
        suggestion_attribute_type = ["style", "material", "theme", "color"]
        attribute_scores = {}
        for x in suggestion_attribute_type:
            attribute_scores[x] = defaultdict(int)

        for suggestion in suggestions:
            for x in suggestion["attributes"]:
                if x["_id"]["type"] in suggestion_attribute_type:
                    attribute_scores[x["_id"]["type"]][x["_id"]["key"]] += 1

        scores = []
        for _type in attribute_scores.keys():
            for key in attribute_scores[_type].keys():
                scores.append(
                    {
                        "key": key,
                        "type": _type,
                        "count": attribute_scores[_type][key]
                    }
                )

        return sorted(scores, key=lambda y: y["count"], reverse=True)

    def data_received(self, chunk):
        pass

