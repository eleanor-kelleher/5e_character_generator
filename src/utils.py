import json


def load_json(file_path: str) -> dict:
    with open(file_path) as file:
        data_dict = json.loads(file.read())
        return data_dict
