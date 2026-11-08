import json
import os


def load_metadata(filepath):
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


def load_table_data(table_name):
    filepath = f"data/{table_name}.json"

    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    os.makedirs("data", exist_ok=True)

    filepath = f"data/{table_name}.json"

    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)