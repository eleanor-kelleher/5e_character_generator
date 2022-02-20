import random

import utils


class Background:
    def __init__(self, bg_name: str, bg_data: dict):
        self.bg_name = bg_name
        print("Background: " + self.bg_name)
        self.skills = bg_data["skills"]
        self.extra_languages = bg_data["languages"]
        self.equipment = self.finalise_equipment_list(bg_data["equipment"])
        self.gp = bg_data["gp"]
        self.proficiencies = bg_data["prof"]
        self.trait = random.choice(bg_data["trait"])
        self.ideal = random.choice(bg_data["ideal"])
        self.bond = random.choice(bg_data["bond"])
        self.flaw = random.choice(bg_data["flaw"])

    @staticmethod
    def finalise_equipment_list(equipment: list):
        final_equip_list = []
        for item in equipment:
            final_equip_list.append(utils.split_on_slash(item))
        return final_equip_list

    def bg_to_dict(self):
        return {
            "Background": self.bg_name,
            "GP": self.gp,
            "PersonalityTraits": self.trait,
            "Ideals": self.ideal,
            "Bonds": self.bond,
            "Flaws": self.flaw,
        }
