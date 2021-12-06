import random

from src import utils


class Race:
    def __init__(self, race_name: str, race_data: dict):
        self.race_name = race_name
        self.mods = race_data["mods"]
        self.speed = race_data["speed"]
        self.languages = race_data["languages"]
        self.extra_languages = race_data["extra languages"]
        self.darkvision = True if race_data["darkvision"] == "yes" else False
        self.skills = race_data["skills"]
        self.skill_number = race_data["skill number"]
        self.proficiencies = race_data["prof"]
        self.features = race_data["features"]
        self.size = race_data["size"]

    def race_to_dict(self):
        return {
            "Race": self.race_name,
            "Speed": self.speed
        }
