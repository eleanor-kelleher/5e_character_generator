import random

from src import utils


class PlayerClass:
    def __init__(self, st_checkboxes: dict, all_items: dict, class_name: str, class_data: dict):
        self.all_items = all_items
        self.st_checkboxes = st_checkboxes
        self.class_name = class_name
        self.level = 1
        self.proficiency_bonus = 2
        self.hit_dice = class_data["hd"]
        self.min_max_stats = class_data["min_max_stats"]
        self.ac = class_data["AC"]
        self.proficiencies = class_data["prof"]
        self.saves = class_data["saves"]
        self.skill_number = class_data["skill number"]
        self.skills = class_data["skills"]
        self.equipment = self.select_item_option(class_data["equipment"])
        self.subclass = (
            random.choice(list(class_data["subclass"]))
            if class_data["subclass"]
            else ""
        )
        self.languages = class_data["languages"]
        self.get_features(class_data)
        self.features = class_data["features"]

    def class_to_dict(self):
        data = {
            "ClassLevel": f"{self.class_name} {self.subclass} {str(self.level)}",
            "HD": "1d" + str(self.hit_dice),
            "HDTotal": str(self.level),
        }
        for st in self.saves:
            data[self.st_checkboxes[st]] = "Yes"
        return data

    def get_features(self, class_data: dict):
        if self.class_name == "Fighter":
            style = random.choice(
                list(class_data["features"]["fighting style"].items())
            )
            class_data["features"].pop("fighting style")
            class_data["features"].update({"Fighting Style: " + style[0]: style[1]})
        elif self.subclass == "Draconic Bloodline":
            self.ac = class_data["subclass"][self.subclass]["AC"]
            self.languages = (
                self.languages + class_data["subclass"][self.subclass]["languages"]
            )
            draconic_type = random.choice(class_data["subclass"][self.subclass]["type"])
            class_data["features"].update({"Draconic Type": draconic_type})
        if self.subclass:
            class_data["features"].update(
                class_data["subclass"][self.subclass]["features"]
            )

    def select_item_option(self, equipment: list) -> list:
        final_list = []
        for item in equipment:
            item = utils.split_on_slash(item)
            item = item.replace("artisan", random.choice(self.all_items["artisan"]))
            item = item.replace("instrument", random.choice(self.all_items["artisan"]))
            simple_melee = "simple melee" in item
            while simple_melee:
                simple_weapon_choice = random.choice(list(self.all_items["weapon"]["simple"].items()))
                if self.all_items["weapon"]["simple"][simple_weapon_choice[0]]["melee"] == "yes":
                    item = item.replace("simple melee", simple_weapon_choice[0], 1)
                    simple_melee = "simple melee" in item
            martial_melee = "simple martial" in item
            while martial_melee:
                martial_weapon_choice = random.choice(self.all_items["weapon"]["martial"])
                if self.all_items["weapon"]["martial"][martial_weapon_choice[0]]["melee"] == "yes":
                    item = item.replace("martial melee", martial_weapon_choice[0], 1)
                    martial_melee = "simple martial" in item
            simple = "simple" in item
            while simple:
                item = item.replace("simple", random.choice(list(self.all_items["weapon"]["simple"])), 1)
                simple = "simple" in item
            martial = "martial" in item
            while martial:
                item = item.replace("martial", random.choice(list(self.all_items["weapon"]["martial"])), 1)
                martial = "martial" in item
            final_list.append(item)
        return final_list
