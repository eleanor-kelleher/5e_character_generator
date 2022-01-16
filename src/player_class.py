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
            if "/" in item:
                item_options = item.split("/")
                item = random.choice(item_options)
            if item == "artisan":
                final_item = random.choice(self.all_items["artisan"])
            elif item == "instrument":
                final_item = random.choice(self.all_items["instrument"])
            elif item == "simple":
                final_item = random.choice(list(self.all_items["weapon"]["simple"]))
            elif item == "martial":
                final_item = random.choice(list(self.all_items["weapon"]["martial"]))
            else:
                final_item = ""
            final_list.append(final_item)
        return final_list
