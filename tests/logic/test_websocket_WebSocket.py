from unittest import TestCase

from mock import Mock

from api.logic.websocket import WebSocket as Target


class write_thinking_message(TestCase):
    def test_no_meta_data(self):
        product_content = Mock()
        client_handlers = {}
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.sender = Mock()
        handler = Mock()
        target.write_thinking_message(handler, "mode_value", None)

        self.assertEqual(1, target.sender.write_to_context_handlers.call_count)
        self.assertEqual(
            handler,
            target.sender.write_to_context_handlers.call_args_list[0][0][0]
        )
        self.assertDictEqual(
            {'thinking_mode': 'mode_value', 'type': 'start_thinking'},
            target.sender.write_to_context_handlers.call_args_list[0][0][1]
        )

    def test_some_meta_data(self):
        product_content = Mock()
        client_handlers = {}
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        handler = Mock()
        target.sender = Mock()
        target.write_thinking_message(handler, "mode_value", "meta_data_value")

        self.assertEqual(1, target.sender.write_to_context_handlers.call_count)
        self.assertEqual(
            handler,
            target.sender.write_to_context_handlers.call_args_list[0][0][0]
        )
        self.assertDictEqual(
            {'meta_data': 'meta_data_value', 'thinking_mode': 'mode_value', 'type': 'start_thinking'},
            target.sender.write_to_context_handlers.call_args_list[0][0][1]
        )


class on_view_product_details_message(TestCase):
    def test_regular(self):
        handler = Mock(name="handler_value")
        handler.context_id = "context_id_value"
        handler.user_id = "user_id_value"
        handler.application_id = "application_id_value"
        handler.session_id = "session_id_value"
        handler.locale = "locale_value"
        handler.suggest_id = "suggest_id_value"
        handler.context_rev = "old_rev"

        product_content = Mock()
        client_handlers = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.post_context_feedback = Mock(
            return_value="new_rev"
        )

        target.on_view_product_details_message(
            handler,
            {
                "product_id": "product_id_value",
                "feedback_type": "type_value"
            }
        )

        self.assertEqual(1, target.post_context_feedback.call_count)
        self.assertEqual("context_id_value", target.post_context_feedback.call_args_list[0][0][0])
        self.assertEqual("user_id_value", target.post_context_feedback.call_args_list[0][0][1])
        self.assertEqual("application_id_value", target.post_context_feedback.call_args_list[0][0][2])
        self.assertEqual("session_id_value", target.post_context_feedback.call_args_list[0][0][3])
        self.assertEqual("product_id_value", target.post_context_feedback.call_args_list[0][0][4])
        self.assertEqual("type_value", target.post_context_feedback.call_args_list[0][0][5])
        self.assertIsNone(target.post_context_feedback.call_args_list[0][0][6])

        self.assertEqual("context_id_value", handler.context_id)
        self.assertEqual("suggest_id_value", handler.suggest_id)
        self.assertEqual("new_rev", handler.context_rev)


class on_new_message(TestCase):
    def test_no_message_no_detected_entities_in_context(self):
        handler = Mock(name="handler_value")
        handler.context_id = "context_id_value"
        handler.user_id = "user_id_value"
        handler.application_id = "application_id_value"
        handler.session_id = "session_id_value"
        handler.locale = "locale_value"
        handler.skip_mongodb_log = "skip_mongodb_log_value"
        handler.page_size = "page_size_value"

        product_content = Mock()
        client_handlers = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.detect.respond_to_detection_response = Mock(
            return_value=None
        )

        target.get_context = Mock(
            return_value={
                "entities": [
                    {
                        "source": "non_detection"
                    }
                ]
            }
        )

        target.post_suggest = Mock(
            return_value="suggest_id_value"
        )

        target.get_suggestion_items = Mock(
            return_value=("suggestions_items_value", "offset_value")
        )

        target.write_suggestion_items = Mock()
        target.write_thinking_message = Mock()

        target.on_new_message(
            handler,
            {
                "message_text": ""
            }
        )

        self.assertEqual(1, target.get_context.call_count)

        self.assertEqual(handler, target.get_context.call_args_list[0][0][0])

        self.assertEqual(1, target.post_suggest.call_count)
        self.assertEqual("user_id_value", target.post_suggest.call_args_list[0][0][0])
        self.assertEqual("application_id_value", target.post_suggest.call_args_list[0][0][1])
        self.assertEqual("session_id_value", target.post_suggest.call_args_list[0][0][2])
        self.assertEqual("locale_value", target.post_suggest.call_args_list[0][0][3])
        self.assertDictEqual(
            {'entities': [{'source': 'non_detection'}]},
            target.post_suggest.call_args_list[0][0][4]
        )

        self.assertEqual(1, target.get_suggestion_items.call_count)
        self.assertEqual("user_id_value", target.get_suggestion_items.call_args_list[0][0][0])
        self.assertEqual("application_id_value", target.get_suggestion_items.call_args_list[0][0][1])
        self.assertEqual("session_id_value", target.get_suggestion_items.call_args_list[0][0][2])
        self.assertEqual("locale_value", target.get_suggestion_items.call_args_list[0][0][3])
        self.assertEqual("suggest_id_value", target.get_suggestion_items.call_args_list[0][0][4])
        self.assertEqual("page_size_value", target.get_suggestion_items.call_args_list[0][0][5])
        self.assertEqual(0, target.get_suggestion_items.call_args_list[0][0][6])

        self.assertEqual("context_id_value", handler.context_id)
        self.assertEqual("suggest_id_value", handler.suggest_id)

        self.assertEqual(1, target.write_suggestion_items.call_count)
        self.assertEqual(handler, target.write_suggestion_items.call_args_list[0][0][0])
        self.assertEqual("suggestions_items_value", target.write_suggestion_items.call_args_list[0][0][1])

        self.assertEqual(2, target.write_thinking_message.call_count)
        self.assertEqual(handler, target.write_thinking_message.call_args_list[0][0][0])
        self.assertEqual("conversation", target.write_thinking_message.call_args_list[0][0][1])

        self.assertEqual(handler, target.write_thinking_message.call_args_list[1][0][0])
        self.assertEqual("suggestions", target.write_thinking_message.call_args_list[1][0][1])

    def test_no_non_detections(self):
        handler = Mock(name="handler_value")
        handler.context_id = "context_id_value"
        handler.user_id = "user_id_value"
        handler.application_id = "application_id_value"
        handler.session_id = "session_id_value"
        handler.locale = "locale_value"
        handler.skip_mongodb_log = "skip_mongodb_log_value"
        handler.page_size = "page_size_value"

        product_content = Mock()
        client_handlers = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.detect.respond_to_detection_response = Mock(
            return_value=None
        )

        target.post_detect = Mock(
            return_value="detection_location_response"
        )
        target.get_detect = Mock(
            return_value="detection_response"
        )
        target.post_context_message_user = Mock(
            return_value="post_context_message_user_context_rev"
        )

        target.get_context = Mock(
            return_value="context_value"
        )

        target.post_suggest = Mock(
            return_value="suggest_id_value"
        )

        target.get_suggestion_items = Mock(
            return_value=("suggestions_items_value", "offset_value")
        )

        target.write_suggestion_items = Mock()
        target.write_thinking_message = Mock()

        target.on_new_message(
            handler,
            {
                "message_text": "message_text_value"
            }
        )

        self.assertEqual(1, target.post_detect.call_count)
        self.assertEqual("user_id_value", target.post_detect.call_args_list[0][0][0])
        self.assertEqual("application_id_value", target.post_detect.call_args_list[0][0][1])
        self.assertEqual("session_id_value", target.post_detect.call_args_list[0][0][2])
        self.assertEqual("locale_value", target.post_detect.call_args_list[0][0][3])
        self.assertEqual("message_text_value", target.post_detect.call_args_list[0][0][4])

        self.assertEqual(1, target.get_detect.call_count)

        self.assertEqual("detection_location_response", target.get_detect.call_args_list[0][0][0])

        self.assertEqual(1, target.detect.respond_to_detection_response.call_count)
        self.assertEqual(handler, target.detect.respond_to_detection_response.call_args_list[0][0][0])
        self.assertEqual("detection_response", target.detect.respond_to_detection_response.call_args_list[0][0][1])

        self.assertEqual(1, target.post_context_message_user.call_count)
        self.assertEqual("context_id_value", target.post_context_message_user.call_args_list[0][0][0])
        self.assertEqual("detection_response", target.post_context_message_user.call_args_list[0][0][1])
        self.assertEqual("message_text_value", target.post_context_message_user.call_args_list[0][0][2])

        self.assertEqual(1, target.get_context.call_count)

        self.assertEqual(handler, target.get_context.call_args_list[0][0][0])

        self.assertEqual(1, target.post_suggest.call_count)
        self.assertEqual("user_id_value", target.post_suggest.call_args_list[0][0][0])
        self.assertEqual("application_id_value", target.post_suggest.call_args_list[0][0][1])
        self.assertEqual("session_id_value", target.post_suggest.call_args_list[0][0][2])
        self.assertEqual("locale_value", target.post_suggest.call_args_list[0][0][3])
        self.assertEqual("context_value", target.post_suggest.call_args_list[0][0][4])

        self.assertEqual(1, target.get_suggestion_items.call_count)
        self.assertEqual("user_id_value", target.get_suggestion_items.call_args_list[0][0][0])
        self.assertEqual("application_id_value", target.get_suggestion_items.call_args_list[0][0][1])
        self.assertEqual("session_id_value", target.get_suggestion_items.call_args_list[0][0][2])
        self.assertEqual("locale_value", target.get_suggestion_items.call_args_list[0][0][3])
        self.assertEqual("suggest_id_value", target.get_suggestion_items.call_args_list[0][0][4])
        self.assertEqual("page_size_value", target.get_suggestion_items.call_args_list[0][0][5])
        self.assertEqual(0, target.get_suggestion_items.call_args_list[0][0][6])

        self.assertEqual("context_id_value", handler.context_id)
        self.assertEqual("post_context_message_user_context_rev", handler.context_rev)
        self.assertEqual("suggest_id_value", handler.suggest_id)

        self.assertEqual(1, target.write_suggestion_items.call_count)
        self.assertEqual(handler, target.write_suggestion_items.call_args_list[0][0][0])
        self.assertEqual("suggestions_items_value", target.write_suggestion_items.call_args_list[0][0][1])

        self.assertEqual(2, target.write_thinking_message.call_count)
        self.assertEqual(handler, target.write_thinking_message.call_args_list[0][0][0])
        self.assertEqual("conversation", target.write_thinking_message.call_args_list[0][0][1])

        self.assertEqual(handler, target.write_thinking_message.call_args_list[1][0][0])
        self.assertEqual("suggestions", target.write_thinking_message.call_args_list[1][0][1])


class on_message(TestCase):
    def test_no_message_type(self):
        product_content = Mock()
        client_handlers = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.on_new_message = Mock()
        target.on_next_page_message = Mock()
        target.on_view_product_details_message = Mock()

        self.assertRaises(
            Exception,
            target.on_message,
            {}
        )

        self.assertEqual(0, target.on_new_message.call_count)
        self.assertEqual(0, target.on_next_page_message.call_count)
        self.assertEqual(0, target.on_view_product_details_message.call_count)

    def test_unknown_message_type(self):
        product_content = Mock()
        client_handlers = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.on_new_message = Mock()
        target.on_next_page_message = Mock()
        target.on_view_product_details_message = Mock()

        self.assertRaises(
            Exception,
            target.on_message,
            {
                "type": "unknown"
            }
        )

        self.assertEqual(0, target.on_new_message.call_count)
        self.assertEqual(0, target.on_next_page_message.call_count)
        self.assertEqual(0, target.on_view_product_details_message.call_count)

    def test_home_page_message(self):
        product_content = Mock()
        client_handlers = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.on_new_message = Mock()
        target.on_next_page_message = Mock()
        target.on_view_product_details_message = Mock()

        target.on_message(
            "handler_value",
            {
                "type": "home_page_message"
            }
        )

        self.assertEqual(1, target.on_new_message.call_count)
        self.assertEqual("handler_value", target.on_new_message.call_args_list[0][0][0])
        self.assertDictEqual(
            {
                "type": "home_page_message"
            },
            target.on_new_message.call_args_list[0][0][1]
        )
        self.assertTrue(
            target.on_new_message.call_args_list[0][1]["new_conversation"]
        )

        self.assertEqual(0, target.on_next_page_message.call_count)
        self.assertEqual(0, target.on_view_product_details_message.call_count)

    def test_new_message(self):
        product_content = Mock()
        client_handlers = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.on_new_message = Mock()
        target.on_next_page_message = Mock()
        target.on_view_product_details_message = Mock()

        target.on_message(
            "handler_value",
            {
                "type": "new_message"
            }
        )

        self.assertEqual(1, target.on_new_message.call_count)
        self.assertEqual("handler_value", target.on_new_message.call_args_list[0][0][0])
        self.assertDictEqual(
            {
                "type": "new_message"
            },
            target.on_new_message.call_args_list[0][0][1]
        )
        self.assertFalse(
            target.on_new_message.call_args_list[0][1]["new_conversation"]
        )

        self.assertEqual(0, target.on_next_page_message.call_count)
        self.assertEqual(0, target.on_view_product_details_message.call_count)

    def test_next_page_message(self):
        product_content = Mock()
        client_handlers = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.on_new_message = Mock()
        target.next_page_message_handler = Mock()
        target.on_view_product_details_message = Mock()

        target.on_message(
            "handler_value",
            {
                "type": "next_page"
            }
        )

        self.assertEqual(0, target.on_new_message.call_count)
        self.assertEqual(1, target.next_page_message_handler.on_next_page_message.call_count)
        self.assertEqual("handler_value", target.next_page_message_handler.on_next_page_message.call_args_list[0][0][0])
        self.assertDictEqual(
            {
                "type": "next_page"
            },
            target.next_page_message_handler.on_next_page_message.call_args_list[0][0][1]
        )

        self.assertEqual(0, target.on_view_product_details_message.call_count)

    def test_view_product_message(self):
        product_content = Mock()
        client_handlers = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.on_new_message = Mock()
        target.on_next_page_message = Mock()
        target.on_view_product_details_message = Mock()

        target.on_message(
            "handler_value",
            {
                "type": "view_product_details"
            }
        )

        self.assertEqual(0, target.on_new_message.call_count)
        self.assertEqual(0, target.on_next_page_message.call_count)

        self.assertEqual(1, target.on_view_product_details_message.call_count)
        self.assertEqual("handler_value", target.on_view_product_details_message.call_args_list[0][0][0])
        self.assertDictEqual(
            {
                "type": "view_product_details"
            },
            target.on_view_product_details_message.call_args_list[0][0][1]
        )


class on_close(TestCase):
    def test_found(self):
        client_handlers = {
            "existing_context_id": {
                "existing_handler_id": "existing_handler"
            },
            "random_context_id": {
                "random_handler_id": "random_handler"
            }
        }
        product_content = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(
            client_handlers=client_handlers,
            product_content=product_content,
            user_info_cache=user_info_cache,
            favorites_cache=favorites_cache

        )
        handler = Mock(name="new_client_handler")
        handler.context_id = "existing_context_id"
        handler.id = "existing_handler_id"
        target.on_close(handler)

        self.assertDictEqual(
            {
                'existing_context_id': {},
                'random_context_id': {'random_handler_id': 'random_handler'}
            },
            client_handlers
        )

    def test_not_found(self):
        client_handlers = {
            "random_id": "other_handler"
        }
        product_content = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(
            client_handlers=client_handlers,
            product_content=product_content,
            user_info_cache=user_info_cache,
            favorites_cache=favorites_cache

        )
        handler = Mock(name="new_client_handler")
        handler.id = "existing_id"
        target.on_close(handler)

        self.assertDictEqual(
            {'random_id': 'other_handler'},
            client_handlers
        )


class open_Tests(TestCase):
    def test_context_id_not_None(self):
        product_content = Mock()
        client_handlers = {}
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)

        handler = Mock(name="new_client_handler")
        handler.id = "new_id"
        handler.context_id = "context_id_value"
        handler.context_rev = "context_rev_value"

        target.open(handler)
        target.post_context = Mock()

        self.assertEqual(0, target.post_context.call_count)

        self.assertEqual("context_rev_value", handler.context_rev)
        self.assertEqual("context_id_value", handler.context_id)

        self.assertEqual(1, handler.write_message.call_count)
        self.assertDictEqual(
            {'context_id': 'context_id_value', 'type': 'connection_opened'},
            handler.write_message.call_args_list[0][0][0]
        )

    def test_context_id_None(self):
        product_content = Mock()
        client_handlers = {}
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)

        target.get_context = Mock()
        target.post_context = Mock(
            return_value=("context_id_value", "context_rev_value")
        )
        handler = Mock()
        handler.context_id = None
        handler.user_id = "user_id_value"
        handler.application_id = "application_id_value"
        handler.session_id = "session_id_value"
        handler.locale = "locale_value"

        target.open(handler)

        self.assertEqual(0, target.get_context.call_count)
        self.assertEqual(1, target.post_context.call_count)

        self.assertEqual("user_id_value", target.post_context.call_args_list[0][0][0])
        self.assertEqual("application_id_value", target.post_context.call_args_list[0][0][1])
        self.assertEqual("session_id_value", target.post_context.call_args_list[0][0][2])
        self.assertEqual("locale_value", target.post_context.call_args_list[0][0][3])

        self.assertEqual("context_id_value", handler.context_id)
        self.assertEqual("context_rev_value", handler.context_rev)

        self.assertEqual(1, handler.write_message.call_count)
        self.assertDictEqual(
            {'context_id': 'context_id_value', 'type': 'connection_opened'},
            handler.write_message.call_args_list[0][0][0]
        )

    def test_new_id(self):
        client_handlers = {
            "different_id": "existing_handler"
        }
        product_content = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)
        target.get_context = Mock(
            return_value="get_context_value"
        )
        target.post_context = Mock()
        handler = Mock(name="new_client_handler")
        handler.id = "new_id"
        handler.context_id = "context_id"
        handler._context = None

        target.open(handler)

        self.assertTrue("context_id" in client_handlers)
        self.assertTrue("new_id" in client_handlers["context_id"])
        self.assertEqual("new_id", client_handlers["context_id"]["new_id"].id)
        self.assertEqual("existing_handler", client_handlers["different_id"])

        self.assertEqual("context_id", handler.context_id)
        self.assertIsNone(handler._context)

        self.assertEqual(0, target.post_context.call_count)

        self.assertEqual(1, handler.write_message.call_count)
        self.assertDictEqual(
            {'context_id': 'context_id', 'type': 'connection_opened'},
            handler.write_message.call_args_list[0][0][0]
        )

    def test_existing_id(self):
        client_handlers = {
            "existing_id": "existing_handler"
        }
        product_content = Mock()
        user_info_cache = Mock()
        favorites_cache = Mock()
        target = Target(product_content=product_content, client_handlers=client_handlers, user_info_cache=user_info_cache, favorites_cache=favorites_cache)


        target.get_context = Mock(
            return_value="get_context_value"
        )
        target.post_context = Mock()
        handler = Mock(name="new_client_handler")
        handler.id = "existing_id"
        handler.context_id = "context_id"
        handler._context = None

        target.open(handler)

        self.assertTrue("existing_id" in client_handlers)
        self.assertEqual("existing_handler", client_handlers["existing_id"])
        self.assertEqual("context_id", handler.context_id)
        self.assertIsNone(handler._context)

        self.assertEqual(0, target.post_context.call_count)

        self.assertEqual(1, handler.write_message.call_count)
        self.assertDictEqual(
            {'context_id': 'context_id', 'type': 'connection_opened'}, handler.write_message.call_args_list[0][0][0]
        )
