from unittest import TestCase

from mock import Mock

from api.logic.suggestions import Suggestions as Target


class fill_suggestions(TestCase):
    def test_regular_user_id(self):
        content = Mock()
        content.get.side_effect = [
            {
                "_id": "new_suggestion_id_value_1"
            },
            {
                "_id": "new_suggestion_id_value_2"
            }
        ]

        favorite_cache = Mock()
        favorite_cache.get.return_value = ["new_suggestion_id_value_1", "not_new_suggestion_id_value_2"]
        target = Target(content, favorite_cache, None)
        target.create_product_url = Mock(return_value="product_url")
        target.get_tile = Mock(
            side_effect=[
                "tile_1",
                "tile_2"
            ]
        )

        actual = target.fill(
            [
                {
                    "_id": "_id_value_1",
                    "score": "suggestion_score_1",
                    "reasons": "suggestion_reasons_1",
                    "index": "suggestion_index_1"
                },
                {
                    "_id": "_id_value_2",
                    "score": "suggestion_score_2",
                    "reasons": "suggestion_reasons_2",
                    "index": "suggestion_index_2"
                }
            ],
            "user_id"
        )
        self.assertListEqual(
            [
                {
                    'tile': 'tile_1', 'score': 'suggestion_score_1', 'favorited': True, 'url': 'product_url',
                    '_id': 'new_suggestion_id_value_1', 'position': 'suggestion_index_1',
                    'reasons': 'suggestion_reasons_1'
                },
                {
                    'tile': 'tile_2', 'score': 'suggestion_score_2', 'favorited': False, 'url': 'product_url',
                    '_id': 'new_suggestion_id_value_2', 'position': 'suggestion_index_2',
                    'reasons': 'suggestion_reasons_2'
                }
            ],
            actual
        )

        self.assertEqual(2, target.get_tile.call_count)
        self.assertDictEqual(
            {
                'position': 'suggestion_index_1', '_id': 'new_suggestion_id_value_1', 'reasons': 'suggestion_reasons_1',
                'score': 'suggestion_score_1', 'favorited': True, 'tile': 'tile_1', 'url': 'product_url'
            },
            target.get_tile.call_args_list[0][0][0]
        )
        self.assertDictEqual(
            {
                'position': 'suggestion_index_2', '_id': 'new_suggestion_id_value_2', 'reasons': 'suggestion_reasons_2',
                'score': 'suggestion_score_2', 'favorited': False, 'tile': 'tile_2', 'url': 'product_url'
            },
            target.get_tile.call_args_list[1][0][0]
        )

        self.assertEqual(2, content.get.call_count)
        self.assertEqual('_id_value_1', content.get.call_args_list[0][0][0])
        self.assertEqual('_id_value_2', content.get.call_args_list[1][0][0])

        self.assertEqual(1, favorite_cache.get.call_count)
        self.assertEqual('user_id', favorite_cache.get.call_args_list[0][0][0])


    def test_user_id_none(self):
        content = Mock()
        content.get.side_effect = [
            {
                "_id": "new_suggestion_id_value_1"
            },
            {
                "_id": "new_suggestion_id_value_2"
            }
        ]

        favorite_cache = Mock()
        favorite_cache.get.return_value = ["new_suggestion_id_value_1", "not_new_suggestion_id_value_2"]
        target = Target(content, favorite_cache, None)
        target.create_product_url = Mock(return_value="product_url")
        target.get_tile = Mock(
            side_effect=[
                "tile_1",
                "tile_2"
            ]
        )

        actual = target.fill(
            [
                {
                    "_id": "_id_value_1",
                    "score": "suggestion_score_1",
                    "reasons": "suggestion_reasons_1",
                    "index": "suggestion_index_1"
                },
                {
                    "_id": "_id_value_2",
                    "score": "suggestion_score_2",
                    "reasons": "suggestion_reasons_2",
                    "index": "suggestion_index_2"
                }
            ],
            None
        )
        self.assertListEqual(
            [
                {
                    'tile': 'tile_1', 'score': 'suggestion_score_1', 'favorited': False, 'url': 'product_url',
                    '_id': 'new_suggestion_id_value_1', 'position': 'suggestion_index_1',
                    'reasons': 'suggestion_reasons_1'
                },
                {
                    'tile': 'tile_2', 'score': 'suggestion_score_2', 'favorited': False, 'url': 'product_url',
                    '_id': 'new_suggestion_id_value_2', 'position': 'suggestion_index_2',
                    'reasons': 'suggestion_reasons_2'
                }
            ],
            actual
        )

        self.assertEqual(2, target.get_tile.call_count)
        self.assertDictEqual(
            {
                'position': 'suggestion_index_1', '_id': 'new_suggestion_id_value_1', 'reasons': 'suggestion_reasons_1',
                'score': 'suggestion_score_1', 'favorited': False, 'tile': 'tile_1', 'url': 'product_url'
            },
            target.get_tile.call_args_list[0][0][0]
        )
        self.assertDictEqual(
            {
                'position': 'suggestion_index_2', '_id': 'new_suggestion_id_value_2', 'reasons': 'suggestion_reasons_2',
                'score': 'suggestion_score_2', 'favorited': False, 'tile': 'tile_2', 'url': 'product_url'
            },
            target.get_tile.call_args_list[1][0][0]
        )

        self.assertEqual(2, content.get.call_count)
        self.assertEqual('_id_value_1', content.get.call_args_list[0][0][0])
        self.assertEqual('_id_value_2', content.get.call_args_list[1][0][0])

        self.assertEqual(0, favorite_cache.get.call_count)
