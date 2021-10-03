import random

from src import utils
from languages import select_languages


class Race:
    def __init__(self):
        self.name, race_data = utils.select_random_from_json("race")
        self.mods = race_data["mods"]
        self.speed = race_data["speed"]
        self.languages = select_languages(
            race_data["extra languages"], race_data["languages"]
        )
        self.darkvision = True if race_data["darkvision"] == "yes" else False
        self.skills = race_data["skills"]
        self.extra_skills = race_data["extra_skills"]
        self.proficiencies = race_data["prof"]
        self.features = race_data["features"]
        self.size = race_data["size"]
