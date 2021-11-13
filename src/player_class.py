import random

from src import utils


class PlayerClass:
    def __init__(self, class_name: str, class_data: dict):
        self.name = class_name
        self.level = 1
        self.hit_dice = "d" + str(class_data["hd"])
        self.min_max_stats = class_data["min_max_stats"]
        self.ac = class_data["AC"]
        self.proficiencies = class_data["prof"]
        self.saves = class_data["saves"]
        self.skill_number = class_data["skill number"]
        self.skills = class_data["skills"]
        self.equipment = self.select_item_option(class_data["equipment"])
        self.subclass = random.choice(list(class_data["subclass"])) if class_data["subclass"] else ""
        self.languages = class_data["languages"]
        self.get_features(class_data)
        self.features = class_data["features"]

    def get_features(self, class_data: dict):
        if self.name == "Fighter":
            style = random.choice(list(class_data["features"]["fighting style"].items()))
            class_data["features"].pop("fighting style")
            class_data["features"].update({"Fighting Style: " + style[0]: style[1]})
        elif self.subclass == "Draconic Bloodline":
            self.ac = class_data["subclass"][self.subclass]["AC"]
            self.languages.append(class_data["subclass"][self.subclass]["languages"])
            draconic_type = random.choice(class_data["subclass"][self.subclass]["type"])
            class_data["features"].update({"Draconic Type": draconic_type})
        if self.subclass:
            class_data["features"].update(class_data["subclass"][self.subclass]["features"])

    @staticmethod
    def select_item_option(equipment: list) -> list:
        final_list = []
        all_items = utils.load_json("../data/items.json")
        for item in equipment:
            if "/" in item:
                item_options = item.split("/")
                item = random.choice(item_options)
            if item == "artisan":
                final_item = random.choice(all_items["artisan"])
            elif item == "instrument":
                final_item = random.choice(all_items["instrument"])
            elif item == "simple":
                final_item = random.choice(list(all_items["weapon"]["simple"]))
            elif item == "martial":
                final_item = random.choice(list(all_items["weapon"]["martial"]))
            else:
                final_item = ""
            final_list.append(final_item)
        return final_list
