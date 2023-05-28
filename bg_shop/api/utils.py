from rest_framework import request as drf_request


def parse_query_params_square_brackets(request: drf_request.Request) -> dict:
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
