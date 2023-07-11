from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from api import utils


class ParseQueryParamsBracketsTestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_parce_nested_key_and_list(self):
        request = self.factory.get(
            "/some/path/?"
            "filter[name]=&filter[minPrice]=0&filter[maxPrice]=50000&"
            "currentPage=1&"
            "tags[]=6&tags[]=7&tags[]=8&"
            "limit=20"
        )

        expected_result = {
            "filter": {"name": "", "minPrice": "0", "maxPrice": "50000", },
            "currentPage": "1",
            "tags": ['6', '7', '8'],
            "limit": '20',
        }
        result = utils.parse_query_params_square_brackets(request)

        self.assertEqual(expected_result, result, "Unexpected result")

    def test_parse_without_query_params(self):
        request = self.factory.get("/some/path")
        result = utils.parse_query_params_square_brackets(request)

        self.assertEqual(
            {}, result, "Unexpected result. Empty dict was expected")
