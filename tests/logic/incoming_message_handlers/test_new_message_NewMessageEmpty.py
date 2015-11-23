from unittest import TestCase

from mock import Mock, MagicMock

from api.logic.incoming_message_handlers import NewMessageEmptyHandler as Target


class on_new_message_empty(TestCase):
    def test_regular(self):
        sender = Mock()
        context = Mock()
        suggest = Mock()
        target = Target(sender, context, suggest)

        handler = Mock()
        handler.user_id = "user_id_value"
        handler.application_id = "application_id_value"
        handler.session_id = "session_id_value"
        handler.locale = "locale_value"

        target.on_new_message_empty(handler, "message_value")

        self.assertEqual(1, context.get_context.call_count)
        self.assertEqual(handler, context.get_context.call_args_list[0][0][0])


class get_context_callback(TestCase):
    def test_regular_has_entities(self):
        sender = MagicMock()
        context = MagicMock()
        suggest = Mock()
        target = Target(sender, context, suggest)

        target.json_decode = MagicMock(
            return_value={
                "entities": [
                    {
                        "source": "non_detection"
                    }
                ],
                "_rev": "_context_rev_value"
            }
        )

        handler = MagicMock()
        handler.user_id = "user_id_value"
        handler.application_id = "application_id_value"
        handler.session_id = "session_id_value"
        handler.locale = "locale_value"

        response = MagicMock()
        response.body = "response_value"
        target.get_context_callback(response, handler, "message_value")

        self.assertEqual(1, suggest.post_suggest.call_count)
        self.assertEqual("user_id_value", suggest.post_suggest.call_args_list[0][0][0])
        self.assertEqual("application_id_value", suggest.post_suggest.call_args_list[0][0][1])
        self.assertEqual("session_id_value", suggest.post_suggest.call_args_list[0][0][2])
        self.assertEqual("locale_value", suggest.post_suggest.call_args_list[0][0][3])
        self.assertDictEqual({'_rev': '_context_rev_value', 'entities': [{'source': 'non_detection'}]},
                             suggest.post_suggest.call_args_list[0][0][4])

        target.json_decode.assert_called_once_with('response_value')

        self.assertDictEqual({'_rev': '_context_rev_value', 'entities': [{'source': 'non_detection'}]}, handler.context)
        self.assertEqual("_context_rev_value", handler.context_rev)


class post_suggest_callback(TestCase):
    def test_regular(self):
        sender = MagicMock()
        context = MagicMock()
        suggest = MagicMock()
        target = Target(sender, context, suggest)
        target.json_decode = MagicMock(return_value={"_rev": "context_revision_value"})

        response = Mock()
        response.headers = {"_id": "suggest_id_value"}
        handler = MagicMock()
        target.post_suggest_callback(response, handler, "message_value")

        suggest.write_new_suggestion.assert_called_once_with(handler)
        self.assertEqual("suggest_id_value", handler.suggest_id)
