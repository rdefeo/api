from unittest import TestCase
from unittest.mock import Mock
from api.logic.ask import Ask as Target
__author__ = 'robdefeo'


class do_Tests(TestCase):
    def test_non_detections(self):
        context = Mock()
        target = Target(context)
        target.get_detection_context = Mock()
        target.get_detection_context.return_value = (
            {
                "_id": "created_context_id"
            },
            {
                "non_detections": "non_detections_value"
            }
        )
        target.get_suggestion = Mock()
        target.get_suggestion.return_value = {
            "suggestions": "suggestions"
        }
        target.fill_suggestions = Mock()
        target.fill_suggestions.return_value = 'filled_suggestions'

        actual = target.do(
            "user_id",
            "session_id",
            "context_id",
            "query",
            "en_UK",
            1,
            10
        )

        self.assertDictEqual(
            actual,
            {
                'context_id': 'created_context_id',
                'page': 1,
                'page_size': 10,
                'non_detections': 'non_detections_value',
                'suggestions': 'filled_suggestions'
            }
        )

        self.assertEqual(
            target.get_detection_context.call_count,
            1
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][0],
            'context_id'
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][1],
            'en_UK'
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][2],
            'query'
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][3],
            'session_id'
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][4],
            'user_id'
        )

        self.assertEqual(
            target.get_suggestion.call_count,
            1
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][0],
            'user_id'
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][1],
            'session_id'
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][2],
            'en_UK'
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][3],
            1
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][4],
            10
        )
        self.assertDictEqual(
            target.get_suggestion.call_args_list[0][0][5],
            {
                '_id': 'created_context_id'
            }
        )

        self.assertEqual(
            target.fill_suggestions.call_count,
            1
        )
        self.assertEqual(
            target.fill_suggestions.call_args_list[0][0][0],
            'suggestions'
        )

    def test_autocorrected(self):
        context = Mock()
        target = Target(context)
        target.get_detection_context = Mock()
        target.get_detection_context.return_value = (
            {
                "_id": "created_context_id"
            },
            {
                "autocorrected": "autocorrected_value"
            }
        )
        target.get_suggestion = Mock()
        target.get_suggestion.return_value = {
            "suggestions": "suggestions"
        }
        target.fill_suggestions = Mock()
        target.fill_suggestions.return_value = 'filled_suggestions'

        actual = target.do(
            "user_id",
            "session_id",
            "context_id",
            "query",
            "en_UK",
            1,
            10
        )

        self.assertDictEqual(
            actual,
            {
                'context_id': 'created_context_id',
                'page': 1,
                'page_size': 10,
                'autocorrected': 'autocorrected_value',
                'suggestions': 'filled_suggestions'
            }
        )

        self.assertEqual(
            target.get_detection_context.call_count,
            1
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][0],
            'context_id'
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][1],
            'en_UK'
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][2],
            'query'
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][3],
            'session_id'
        )
        self.assertEqual(
            target.get_detection_context.call_args_list[0][0][4],
            'user_id'
        )

        self.assertEqual(
            target.get_suggestion.call_count,
            1
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][0],
            'user_id'
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][1],
            'session_id'
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][2],
            'en_UK'
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][3],
            1
        )
        self.assertEqual(
            target.get_suggestion.call_args_list[0][0][4],
            10
        )
        self.assertDictEqual(
            target.get_suggestion.call_args_list[0][0][5],
            {
                '_id': 'created_context_id'
            }
        )

        self.assertEqual(
            target.fill_suggestions.call_count,
            1
        )
        self.assertEqual(
            target.fill_suggestions.call_args_list[0][0][0],
            'suggestions'
        )


class build_header_link_Tests(TestCase):
    def test_regular(self):
        context = Mock()
        target = Target(context)
        actual = target.build_header_link("href_value", "relationship_value")
        self.assertEqual(
            actual,
            '<href_value>; rel="relationship_value"'
        )