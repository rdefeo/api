from unittest import TestCase

from mock import Mock

from api.logic.incoming_message_handlers import NextPageMessageHandler as Target


class on_next_page_message(TestCase):
    def test_regular(self):
        handler = Mock(name="handler_value")
        handler.context_id = "context_id_value"
        handler.user_id = "user_id_value"
        handler.application_id = "application_id_value"
        handler.session_id = "session_id_value"
        handler.locale = "locale_value"
        handler.suggest_id = "suggest_id_value"
        handler.page_size = "page_size_value"

        suggestions = Mock()
        target = Target(suggestions)

        target.on_next_page_message(
            handler,
            {
                "suggest_id": "suggest_id_value",
                "offset": "original_offset_value"
            }
        )

        self.assertEqual(1, target.suggestions.get_suggestion_items.call_count)
        self.assertEqual("user_id_value", target.suggestions.get_suggestion_items.call_args_list[0][0][0])
        self.assertEqual("application_id_value", target.suggestions.get_suggestion_items.call_args_list[0][0][1])
        self.assertEqual("session_id_value", target.suggestions.get_suggestion_items.call_args_list[0][0][2])
        self.assertEqual("locale_value", target.suggestions.get_suggestion_items.call_args_list[0][0][3])
        self.assertEqual("suggest_id_value", target.suggestions.get_suggestion_items.call_args_list[0][0][4])
        self.assertEqual("page_size_value", target.suggestions.get_suggestion_items.call_args_list[0][0][5])
        self.assertEqual("original_offset_value", target.suggestions.get_suggestion_items.call_args_list[0][0][6])

        self.assertEqual("context_id_value", handler.context_id)
        self.assertEqual("suggest_id_value", handler.suggest_id)
