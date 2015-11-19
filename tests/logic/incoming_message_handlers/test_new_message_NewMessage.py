from unittest import TestCase

from mock import Mock

from api.logic.incoming_message_handlers import NewMessageHandler as Target
from api.logic.incoming_message_handlers import NewMessageTextHandler, NewMessageEmptyHandler


class on_new_message(TestCase):
    def test_no_message_text(self):
        sender = Mock()
        target = Target(sender, Mock, Mock(), Mock())
        target.new_message_empty_handler = Mock(spec=NewMessageEmptyHandler)
        target.on_new_message("handler_value", {"message_text": ""})

        self.assertEqual(2, sender.write_thinking_message.call_count)
        self.assertEqual("handler_value", sender.write_thinking_message.call_args_list[0][0][0])
        self.assertEqual("conversation", sender.write_thinking_message.call_args_list[0][0][1])
        self.assertEqual("handler_value", sender.write_thinking_message.call_args_list[1][0][0])
        self.assertEqual("suggestions", sender.write_thinking_message.call_args_list[1][0][1])

        self.assertEqual(1, target.new_message_empty_handler.on_new_message_empty.call_count)
        self.assertEqual("handler_value", target.new_message_empty_handler.on_new_message_empty.call_args_list[0][0][0])
        self.assertDictEqual({'message_text': ''}, target.new_message_empty_handler.on_new_message_empty.call_args_list[0][0][1])

    def test_has_message_text(self):
        sender = Mock()
        target = Target(sender, Mock, Mock(), Mock())
        target.new_message_text_handler = Mock(spec=NewMessageTextHandler)
        target.on_new_message("handler_value", {"message_text": "message_text_value"})

        self.assertEqual(2, sender.write_thinking_message.call_count)
        self.assertEqual("handler_value", sender.write_thinking_message.call_args_list[0][0][0])
        self.assertEqual("conversation", sender.write_thinking_message.call_args_list[0][0][1])
        self.assertEqual("handler_value", sender.write_thinking_message.call_args_list[1][0][0])
        self.assertEqual("suggestions", sender.write_thinking_message.call_args_list[1][0][1])

        self.assertEqual(1, target.new_message_text_handler.on_new_message_text.call_count)
        self.assertEqual("handler_value", target.new_message_text_handler.on_new_message_text.call_args_list[0][0][0])
        self.assertDictEqual({'message_text': 'message_text_value'}, target.new_message_text_handler.on_new_message_text.call_args_list[0][0][1])
        self.assertEqual("message_text_value", target.new_message_text_handler.on_new_message_text.call_args_list[0][0][2])


