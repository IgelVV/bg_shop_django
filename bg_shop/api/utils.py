from rest_framework import request as drf_request


def nested_query_params_parser(request: drf_request.Request) -> dict:
    data = {}
    for key, value in request.query_params.items():
        if '[' in key and ']' in key:
            # nested
            index_left_bracket = key.index('[')
            index_right_bracket = key.index(']')
            nested_dict_key = key[:index_left_bracket]
            nested_value_key = key[index_left_bracket + 1:index_right_bracket]
            if nested_dict_key not in data:
                data[nested_dict_key] = {}
            data[nested_dict_key][nested_value_key] = value
        else:
            data[key] = value
    return data
