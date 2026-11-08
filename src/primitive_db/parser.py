def parse_columns(arguments):
    columns = {}

    for argument in arguments:
        if ":" not in argument:
            raise ValueError(f"Некорректный столбец: {argument}.")

        column_name, column_type = argument.split(":", 1)

        column_name = column_name.strip()
        column_type = column_type.strip()

        if not column_name or not column_type:
            raise ValueError(f"Некорректный столбец: {argument}.")

        if column_name in columns:
            raise ValueError(f'Столбец "{column_name}" уже существует.')

        columns[column_name] = column_type

    return columns


def parse_value(value):
    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        return value


def parse_condition(condition):
    if "=" not in condition:
        raise ValueError(f"Некорректное условие: {condition}.")

    column, value = condition.split("=", 1)

    column = column.strip()
    value = value.strip()

    if not column or not value:
        raise ValueError(f"Некорректное условие: {condition}.")

    return {column: parse_value(value)}


def parse_set_clause(arguments):
    result = {}

    arguments_text = " ".join(arguments)
    assignments = arguments_text.split(",")

    for assignment in assignments:
        if "=" not in assignment:
            raise ValueError(
                f"Некорректное выражение: {assignment}."
            )

        column, value = assignment.split("=", 1)

        column = column.strip()
        value = value.strip()

        if not column or not value:
            raise ValueError(
                f"Некорректное выражение: {assignment}."
            )

        result[column] = parse_value(value)

    return result