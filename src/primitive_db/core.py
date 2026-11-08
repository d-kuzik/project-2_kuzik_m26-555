from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

select_cache = create_cacher()


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    table_columns = {"ID": "int"}

    for column_name, column_type in columns.items():
        if column_name == "ID":
            raise ValueError('Имя столбца "ID" зарезервировано.')

        if column_type not in VALID_TYPES:
            raise ValueError(f"Некорректный тип: {column_type}.")

        if column_name in table_columns:
            raise ValueError(f'Столбец "{column_name}" уже существует.')

        table_columns[column_name] = column_type

    metadata[table_name] = {
        "columns": table_columns,
    }

    return metadata


@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]

    return metadata


def list_tables(metadata):
    return list(metadata.keys())


@log_time
def insert(metadata, table_name, values, table_data):
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    columns = metadata[table_name]["columns"]
    column_names = list(columns.keys())

    if len(values) != len(column_names) - 1:
        raise ValueError("Некорректное количество значений.")

    for value, column_name in zip(values, column_names[1:]):
        column_type = columns[column_name]

        if column_type == "int" and (
            not isinstance(value, int) or isinstance(value, bool)
        ):
            raise ValueError(f"Некорректное значение: {value}.")

        if column_type == "str" and not isinstance(value, str):
            raise ValueError(f"Некорректное значение: {value}.")

        if column_type == "bool" and not isinstance(value, bool):
            raise ValueError(f"Некорректное значение: {value}.")

    new_id = max((row["ID"] for row in table_data), default=0) + 1

    row = {"ID": new_id}

    for column_name, value in zip(column_names[1:], values):
        row[column_name] = value

    table_data.append(row)

    return table_data


@confirm_action("удаление записей")
def delete(table_data, where_clause):
    result = []

    for row in table_data:
        matches = True

        for column, value in where_clause.items():
            if column not in row or row[column] != value:
                matches = False
                break

        if not matches:
            result.append(row)

    return result


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    cache_key = repr((table_data, where_clause))

    def get_result():
        if where_clause is None:
            return list(table_data)

        result = []

        for row in table_data:
            matches = True

            for column, value in where_clause.items():
                if column not in row or row[column] != value:
                    matches = False
                    break

            if matches:
                result.append(row)

        return result

    return select_cache(cache_key, get_result)


def update(table_data, set_clause, where_clause):
    updated_rows = []

    for row in table_data:
        matches = True

        for column, value in where_clause.items():
            if column not in row or row[column] != value:
                matches = False
                break

        if matches:
            for column, value in set_clause.items():
                if column not in row:
                    raise KeyError(
                        f'Столбец "{column}" не существует.'
                    )

                row[column] = value

        updated_rows.append(row)

    return updated_rows
