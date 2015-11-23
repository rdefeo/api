from unittest import TestCase

from mock import Mock, MagicMock

from api.logic.incoming_message_handlers import NewMessageTextHandler as Target


class on_new_message(TestCase):
    def test_regular(self):
        sender = Mock()
        detect = Mock()
        context = Mock()
        suggest = Mock()
        target = Target(sender, detect, context, suggest)

        handler = Mock()
        handler.user_id = "user_id_value"
        handler.application_id = "application_id_value"
        handler.session_id = "session_id_value"
        handler.locale = "locale_value"

        target.on_new_message_text(handler, "message_value", "message_text_value")

        self.assertEqual(1, detect.post_detect.call_count)
        self.assertEqual("user_id_value", detect.post_detect.call_args_list[0][0][0])
        self.assertEqual("application_id_value", detect.post_detect.call_args_list[0][0][1])
        self.assertEqual("session_id_value", detect.post_detect.call_args_list[0][0][2])
        self.assertEqual("locale_value", detect.post_detect.call_args_list[0][0][3])
        self.assertEqual("message_text_value", detect.post_detect.call_args_list[0][0][4])


class post_detect_callback(TestCase):
    def test_post_detect_callback(self):
        sender = Mock()
        detect = Mock()
        context = Mock()
        suggest = Mock()
        target = Target(sender, detect, context, suggest)

        response = Mock()
        response.headers = {"Location": "location_value"}
        target.post_detect_callback(response, "handler", "message_value")

        self.assertEqual(1, target.detect.get_detect.call_count)
        self.assertEqual("location_value", target.detect.get_detect.call_args_list[0][0][0])


class get_detect_callback(TestCase):
    def test_no_respond_to_detection_response(self):
        sender = MagicMock()
        detect = MagicMock()
        context = MagicMock()
        suggest = Mock()
        target = Target(sender, detect, context, suggest)
        target.json_decode = MagicMock(return_value="decode_detection_response")

        response = Mock()
        response.body = "response_body"

        handler = Mock()
        handler.context_id = "context_id_value"

        target.get_detect_callback(response, handler, "message_value")

        target.json_decode.assert_called_once_with("response_body")

        # context.post_context_message.assert_called_once_with("context_id_value", 1, "", dection="decode_detection_response")

        self.assertEqual(1, context.post_context_message.call_count)
        self.assertEqual("context_id_value", context.post_context_message.call_args_list[0][0][0])
        self.assertEqual(1, context.post_context_message.call_args_list[0][0][1])
        self.assertEqual("", context.post_context_message.call_args_list[0][0][2])
        self.assertEqual("decode_detection_response", context.post_context_message.call_args_list[0][1]["detection"])

        detect.respond_to_detection_response.assert_called_once_with(handler, "decode_detection_response")

        sender.write_jemboo_response_message.assert_not_called()

    def test_respond_to_detection_response(self):
        sender = MagicMock()
        detect = MagicMock()
        detect.respond_to_detection_response = Mock(return_value="something_to_send")
        context = MagicMock()
        suggest = Mock()
        target = Target(sender, detect, context, suggest)
        target.json_decode = MagicMock(return_value="decode_detection_response")

        response = Mock()
        response.body = "response_body"

        handler = Mock()
        handler.context_id = "context_id_value"

        target.get_detect_callback(response, handler, "message_value")

        target.json_decode.assert_called_once_with("response_body")

        # context.post_context_message.assert_called_once_with("context_id_value", 1, "", dection="decode_detection_response")

        self.assertEqual(1, context.post_context_message.call_count)
        self.assertEqual("context_id_value", context.post_context_message.call_args_list[0][0][0])
        self.assertEqual(1, context.post_context_message.call_args_list[0][0][1])
        self.assertEqual("", context.post_context_message.call_args_list[0][0][2])
        self.assertEqual("decode_detection_response", context.post_context_message.call_args_list[0][1]["detection"])

        detect.respond_to_detection_response.assert_called_once_with(handler, "decode_detection_response")

        sender.write_jemboo_response_message.assert_called_once_with(handler, "something_to_send")


class get_context_callback(TestCase):
    def test_regular(self):
        sender = MagicMock()
        detect = MagicMock()
        context = MagicMock()
        suggest = Mock()
        target = Target(sender, detect, context, suggest)

        target.post_context_message_callback("response_value", "handler_value", "message_value")

        self.assertEqual(1, context.get_context.call_count)
        self.assertEqual("handler_value", context.get_context.call_args_list[0][0][0])


class post_context_message_user_callback(TestCase):
    def test_regular(self):
        sender = MagicMock()
        detect = MagicMock()
        context = MagicMock()
        suggest = Mock()
        target = Target(sender, detect, context, suggest)
        target.json_decode = MagicMock(return_value={"_rev": "context_revision_value"})
        target.context_responder.unsupported_entities = MagicMock()

        response = Mock()
        response.body = "response_body_value"

        handler = MagicMock()
        handler.user_id = "user_id_value"
        handler.application_id = "application_id_value"
        handler.session_id = "session_id_value"
        handler.locale = "locale_value"

        target.get_context_callback(response, handler, "message_value")

        target.json_decode.assert_called_once_with("response_body_value")

        target.context_responder.unsupported_entities.assert_called_once_with(handler,
                                                                              {'_rev': 'context_revision_value'})

        self.assertEqual(1, suggest.post_suggest.call_count)
        self.assertEqual("user_id_value", suggest.post_suggest.call_args_list[0][0][0])
        self.assertEqual("application_id_value", suggest.post_suggest.call_args_list[0][0][1])
        self.assertEqual("session_id_value", suggest.post_suggest.call_args_list[0][0][2])
        self.assertEqual("locale_value", suggest.post_suggest.call_args_list[0][0][3])
        self.assertDictEqual({'_rev': 'context_revision_value'}, suggest.post_suggest.call_args_list[0][0][4])


class post_suggest_callback(TestCase):
    def test_regular(self):
        sender = MagicMock()
        detect = MagicMock()
        context = MagicMock()
        suggest = MagicMock()
        target = Target(sender, detect, context, suggest)
        target.json_decode = MagicMock(return_value={"_rev": "context_revision_value"})

        response = Mock()
        response.headers = {"_id": "suggest_id_value"}
        handler = MagicMock()
        target.post_suggest_callback(response, handler, "message_value")

        suggest.write_new_suggestion.assert_called_once_with(handler)
        self.assertEqual("suggest_id_value", handler.suggest_id)
