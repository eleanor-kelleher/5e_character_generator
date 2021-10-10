import json
import random


def load_json(file_path: str) -> dict:
    with open(file_path) as file:
        data_dict = json.loads(file.read())
        return data_dict


def select_random_from_json(json_file: str):
    all_options = load_json(json_file)
    return random.choice(list(all_options.items()))
