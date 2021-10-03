import random

from src import utils


def select_languages(count: int, already_known: list):
    all_languages = utils.load_json("../data/languages.json")
    if len(already_known) + count >= len(all_languages):
        return all_languages
    while count > 0:
        current_lang = random.choice(all_languages)
        if current_lang not in already_known:
            already_known.append(current_lang)
            count = count - 1
    return already_known
