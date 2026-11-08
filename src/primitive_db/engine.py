import shlex

from prettytable import PrettyTable

from primitive_db.constants import META_FILE
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import (
    parse_columns,
    parse_condition,
    parse_set_clause,
    parse_value,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def welcome():
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    print("Введите команду: ", end="")


def run():
    welcome()

    while True:
        user_input = input()

        if not user_input.strip():
            print("Введите команду: ", end="")
            continue

        command = shlex.split(user_input)

        if command[0] == "exit":
            break

        elif command[0] == "help":
            print("Справочная информация")

        elif command[0] == "create_table":
            if len(command) < 3:
                print("Некорректная команда. Попробуйте снова.")
                continue

            table_name = command[1]

            try:
                columns = parse_columns(command[2:])
                metadata = load_metadata(META_FILE)
                metadata = create_table(metadata, table_name, columns)
                save_metadata(META_FILE, metadata)

                columns_text = ", ".join(
                    f"{name}:{column_type}"
                    for name, column_type in metadata[table_name][
                        "columns"
                    ].items()
                )

                print(
                    f'Таблица "{table_name}" успешно создана '
                    f"со столбцами: {columns_text}"
                )

            except (KeyError, ValueError, FileNotFoundError) as error:
                print(error)

        elif command[0] == "list_tables":
            metadata = load_metadata(META_FILE)

            if not metadata:
                print("Таблиц нет.")
            else:
                for table_name in list_tables(metadata):
                    print(f"- {table_name}")

        elif command[0] == "drop_table":
            if len(command) != 2:
                print("Некорректная команда. Попробуйте снова.")
                continue

            table_name = command[1]

            try:
                metadata = load_metadata(META_FILE)
                metadata = drop_table(metadata, table_name)
                save_metadata(META_FILE, metadata)

                print(f'Таблица "{table_name}" успешно удалена.')

            except (KeyError, ValueError, FileNotFoundError) as error:
                print(error)

        elif command[0] == "insert":
            if len(command) < 5:
                print("Некорректная команда. Попробуйте снова.")
                continue

            if command[1].lower() != "into":
                print("Некорректная команда. Попробуйте снова.")
                continue

            table_name = command[2]

            if command[3].lower() != "values":
                print("Некорректная команда. Попробуйте снова.")
                continue

            try:
                values_text = " ".join(command[4:]).strip()

                if not (
                    values_text.startswith("(")
                    and values_text.endswith(")")
                ):
                    raise ValueError("Некорректные значения.")

                values_text = values_text[1:-1]

                raw_values = [
                    value.strip()
                    for value in values_text.split(",")
                ]

                if any(not value for value in raw_values):
                    raise ValueError("Некорректные значения.")

                values = [parse_value(value) for value in raw_values]

                metadata = load_metadata(META_FILE)
                table_data = load_table_data(table_name)

                table_data = insert(
                    metadata,
                    table_name,
                    values,
                    table_data,
                )

                save_table_data(table_name, table_data)

                print(
                    f'Запись успешно добавлена в таблицу "{table_name}".'
                )

            except (KeyError, ValueError, FileNotFoundError) as error:
                print(error)

        elif command[0] == "select":
            if len(command) < 3:
                print("Некорректная команда. Попробуйте снова.")
                continue

            if command[1].lower() != "from":
                print("Некорректная команда. Попробуйте снова.")
                continue

            table_name = command[2]

            try:
                metadata = load_metadata(META_FILE)

                if table_name not in metadata:
                    raise KeyError(
                        f'Таблица "{table_name}" не существует.'
                    )

                table_data = load_table_data(table_name)

                where_clause = None

                if len(command) > 3:
                    if (
                        len(command) < 6
                        or command[3].lower() != "where"
                    ):
                        print("Некорректная команда. Попробуйте снова.")
                        continue

                    condition = " ".join(command[4:])
                    where_clause = parse_condition(condition)

                result = select(table_data, where_clause)

                if not result:
                    print("Записей нет.")
                    continue

                table = PrettyTable()
                table.field_names = list(
                    metadata[table_name]["columns"].keys()
                )

                for row in result:
                    table.add_row(
                        [row[column] for column in table.field_names]
                    )

                print(table)

            except (KeyError, ValueError, FileNotFoundError) as error:
                print(error)

        elif command[0] == "delete":
            if len(command) < 5:
                print("Некорректная команда. Попробуйте снова.")
                continue

            table_name = command[1]

            if command[2].lower() != "where":
                print("Некорректная команда. Попробуйте снова.")
                continue

            try:
                metadata = load_metadata(META_FILE)

                if table_name not in metadata:
                    raise KeyError(
                        f'Таблица "{table_name}" не существует.'
                    )

                condition = " ".join(command[3:])
                where_clause = parse_condition(condition)

                table_data = load_table_data(table_name)
                table_data = delete(table_data, where_clause)

                save_table_data(table_name, table_data)

                print(
                    f'Записи из таблицы "{table_name}" успешно удалены.'
                )

            except (KeyError, ValueError, FileNotFoundError) as error:
                print(error)

        elif command[0] == "info":
            if len(command) != 2:
                print("Некорректная команда. Попробуйте снова.")
                continue

            table_name = command[1]

            try:
                metadata = load_metadata(META_FILE)

                if table_name not in metadata:
                    raise KeyError(
                        f'Таблица "{table_name}" не существует.'
                    )

                table_data = load_table_data(table_name)

                table = PrettyTable()
                table.field_names = ["Столбец", "Тип"]

                for column_name, column_type in metadata[
                    table_name
                ]["columns"].items():
                    table.add_row([column_name, column_type])

                print(f'Информация о таблице "{table_name}":')
                print(table)
                print(f"Количество записей: {len(table_data)}")

            except (KeyError, ValueError, FileNotFoundError) as error:
                print(error)

        elif command[0] == "update":
            if len(command) < 7:
                print("Некорректная команда. Попробуйте снова.")
                continue

            table_name = command[1]

            if command[2].lower() != "set":
                print("Некорректная команда. Попробуйте снова.")
                continue

            if "where" not in command:
                print("Некорректная команда. Попробуйте снова.")
                continue

            where_index = command.index("where")

            set_arguments = command[3:where_index]
            condition_arguments = command[where_index + 1:]

            try:
                set_clause = parse_set_clause(set_arguments)

                condition = " ".join(condition_arguments)
                where_clause = parse_condition(condition)

                metadata = load_metadata(META_FILE)

                if table_name not in metadata:
                    raise KeyError(
                        f'Таблица "{table_name}" не существует.'
                    )

                table_data = load_table_data(table_name)

                table_data = update(
                    table_data,
                    set_clause,
                    where_clause,
                )

                save_table_data(table_name, table_data)

                print(
                    f'Таблица "{table_name}" успешно обновлена.'
                )

            except (KeyError, ValueError, FileNotFoundError) as error:
                print(error)

        else:
            print(f"Функции {command[0]} нет. Попробуйте снова.")

        print("Введите команду: ", end="")
