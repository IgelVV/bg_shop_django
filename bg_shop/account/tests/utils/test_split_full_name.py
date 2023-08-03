from django.test import TestCase

from account import utils


class SplitFullNameTestCase(TestCase):
    def test_more_than_two_parts(self):
        full_name = "first second last"

        with self.assertRaises(
                ValueError, msg="Exception hasn't been raised."):
            utils.split_full_name(full_name)

    def test_split_correctly_two_parts(self):
        first = "first"
        last = "last"
        full_name = "  " + first + "   " + last + "  "
        self.assertEqual(
            [first, last],
            utils.split_full_name(full_name),
            "Wrong splitting."
        )


