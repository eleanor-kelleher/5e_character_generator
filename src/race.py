import random

from src import utils
from languages import select_languages


class Race:
    def __init__(self):
        self.name, race_data = self.select_random_race()
        self.mods = race_data["mods"]
        self.speed = race_data["speed"]
        self.languages = select_languages(
            race_data["extra_languages"], race_data["languages"]
        )
        self.darkvision = True if race_data["darkvision"] == "yes" else False
        self.skills = race_data["skills"]
        self.extra_skills = race_data["extra_skills"]
        self.proficiencies = race_data["prof"]
        self.features = race_data["features"]
        self.size = race_data["size"]

    def select_random_race(self) -> (str, dict):
        all_races = utils.load_json("../data/races.json")
        race_name = random.choice(all_races)
        return race_name, all_races[race_name]
