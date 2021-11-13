import random


class Background:
    def __init__(self, bg_name: str, bg_data: dict):
        self.name = bg_name
        self.skills = bg_data["skills"]
        self.extra_languages = bg_data["languages"]
        self.equipment = bg_data["equipment"]
        self.gp = bg_data["gp"]
        self.proficiencies = bg_data["prof"]
        self.trait = random.choice(bg_data["trait"])
        self.ideal = random.choice(bg_data["ideal"])
        self.bond = random.choice(bg_data["bond"])
        self.flaw = random.choice(bg_data["flaw"])
