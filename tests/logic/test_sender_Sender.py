from unittest import TestCase

from mock import Mock

from api.logic.sender import Sender as Target

__author__ = 'robdefeo'


class write_jemboo_response_message(TestCase):
    def test_regular(self):
        target = Target("client_handlers_value")
        target.write_to_context_handlers = Mock()

        target.write_jemboo_response_message(
            "handler_value",
            {
                "type": "message_type",
                "direction": 0
            }
        )

        self.assertEqual(1, target.write_to_context_handlers.call_count)
        self.assertEqual("handler_value", target.write_to_context_handlers.call_args_list[0][0][0])
        self.assertDictEqual(
            {'type': 'jemboo_chat_response', 'direction': 0},
            target.write_to_context_handlers.call_args_list[0][0][1])
