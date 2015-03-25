from unittest import TestCase
from unittest.mock import Mock
from api.logic.ask import Ask as Target
__author__ = 'robdefeo'


class build_header_link_Tests(TestCase):
    def test_regular(self):
        context = Mock()
        target = Target(context)
        actual = target.build_header_link("href_value", "relationship_value")
        self.assertEqual(
            actual,
            '<href_value>; rel="relationship_value"'
        )