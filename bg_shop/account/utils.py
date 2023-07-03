"""Useful functions related to account data."""


def split_full_name(full_name: str) -> list[str]:
    """
    Split the full name into two parts.

    If there are more parts separated by ' '(whitespace) raises ValueError
    :param full_name: first_name_string + last_name_string
    :return: [first_name, last_name]
    """
    result = full_name.split(' ')
    if len(result) > 2:
        raise ValueError("The full_name contains more than two parts")
    return result
