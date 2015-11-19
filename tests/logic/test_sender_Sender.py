from unittest import TestCase

from mock import Mock

from api.logic.sender import Sender as Target

__author__ = 'robdefeo'


class write_thinking_message(TestCase):
    def test_no_meta_data(self):
        client_handlers = {}
        target = Target(client_handlers=client_handlers)
        target.write_to_context_handlers = Mock()
        handler = Mock()
        target.write_thinking_message(handler, "mode_value", None)

        self.assertEqual(1, target.write_to_context_handlers.call_count)
        self.assertEqual(
            handler,
            target.write_to_context_handlers.call_args_list[0][0][0]
        )
        self.assertDictEqual(
            {'thinking_mode': 'mode_value', 'type': 'start_thinking'},
            target.write_to_context_handlers.call_args_list[0][0][1]
        )

    def test_some_meta_data(self):
        client_handlers = {}
        target = Target(client_handlers=client_handlers)
        handler = Mock()
        target.write_to_context_handlers = Mock()
        target.write_thinking_message(handler, "mode_value", "meta_data_value")

        self.assertEqual(1, target.write_to_context_handlers.call_count)
        self.assertEqual(
            handler,
            target.write_to_context_handlers.call_args_list[0][0][0]
        )
        self.assertDictEqual(
            {'meta_data': 'meta_data_value', 'thinking_mode': 'mode_value', 'type': 'start_thinking'},
            target.write_to_context_handlers.call_args_list[0][0][1]
        )



class write_jemboo_response_message(TestCase):
    def test_regular(self):
        target = Target("client_handlers_value")
        target.post_suggest_callback = Mock()

        target.context = Mock()
        handler = Mock()
        handler.context_id = "context_id_value"

        target.write_jemboo_response_message(
            handler,
            {
                "type": "message_type",
                "direction": 0,
                "display_text": "display_text_value"
            }
        )

        self.assertEqual(1, target.context.post_context_message.call_count)
        self.assertEqual("context_id_value", target.context.post_context_message.call_args_list[0][0][0])
        self.assertEqual(0, target.context.post_context_message.call_args_list[0][0][1])
        self.assertEqual("display_text_value", target.context.post_context_message.call_args_list[0][0][2])

        # self.assertEqual(1, target.post_suggest_callback.call_count)
