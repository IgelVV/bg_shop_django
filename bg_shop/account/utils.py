def split_full_name(full_name: str) -> list[str]:
    """
    Splits the full name into two parts,
    if there are more parts separated by ' '(whitespace) raises ValueError
    :param full_name: first_name_string + last_name_string
    :return: [first_name, last_name]
    """
    result = full_name.split(' ')
    if len(result) > 2:
        raise ValueError("The full_name contains more than two parts")
    return result
