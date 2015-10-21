from unittest import TestCase

from mock import Mock

from api.logic.sender import Sender as Target

__author__ = 'robdefeo'


class write_jemboo_response_message(TestCase):
    def test_regular(self):
        target = Target("client_handlers_value")
        target.write_to_context_handlers = Mock()
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
