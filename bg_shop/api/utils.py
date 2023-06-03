from rest_framework import request as drf_request


def parse_query_params_square_brackets(request: drf_request.Request) -> dict:
    """
    Creates dict based on query params. Parses maps and arrays that use
    square bracket notation.
    Example:
        Query string params:
            /?filter[name]=&filter[minPrice]=0&filter[maxPrice]=50000&
            currentPage=1&
            tags[]=6&tags[]=7&tags[]=8&
            limit=20
        DRF Request.query_params:
            <QueryDict: {
            'filter[name]':[''], 'filter[minPrice]':['0'], 'filter[maxPrice]':['50000'],
            'currentPage': ['1'],
            'tags[]': ['6', '7', '8'],
            'limit': ['20']}>
        result:
            {
                "filter": {"name": "", "minPrice": "0", "maxPrice": "50000",},
                "currentPage": "1",
                "tags": ['6', '7', '8'],
                "limit": '20',
            }
    :param request: to parse query parameters from
    :return: dict with nested dicts and lists if they are passed in query
    """
    data = {}
    for key, value in request.query_params.items():
        if '[' in key and ']' in key:
            # nested
            index_left_bracket = key.index('[')
            index_right_bracket = key.index(']')
            main_key = key[:index_left_bracket]
            nested_key = key[index_left_bracket + 1:index_right_bracket]
            if nested_key:
                if main_key not in data:
                    data[main_key] = {}
                data[main_key][nested_key] = value
            else:
                if main_key not in data:
                    data[main_key] = request.query_params.getlist(key)
        else:
            data[key] = value
    return data
