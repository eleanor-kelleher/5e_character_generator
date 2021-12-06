import json
import random


def load_json(file_path: str) -> dict:
    with open(file_path) as file:
        x = json.loads(file.read())
        return x


def select_random_from_json(json_file: str):
    all_options = load_json(json_file)
    return random.choice(list(all_options.items()))


def dict_to_string(d: dict):
    s = ""
    for key in d:
        s = f"{s}{key}: {d[key]}\n"
    return s
