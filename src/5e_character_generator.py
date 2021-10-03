import json

import names
import pdfrw
import random
import yaml

import dice
import mods

from race import Race
from background import Background
from player_class import PlayerClass
from weapon import Weapon

# STATICS
BLANK_CHAR_SHEET = "pdfs/Character Sheet - Form Fillable.pdf"
OUTPUT_CHAR_SHEET = "pdfs/Character_Sheet_Output.pdf"
RACE_PATH = "../data/races.json"
BACKGROUND_PATH = "../data/backgrounds.json"
CLASS_PATH = "../data/classes.json"
ITEM_PATH = "../data/items.json"


def load_json(file_path: str) -> dict:
    with open(file_path) as file:
        data_dict = json.loads(file.read())
        return data_dict


class CharacterSheet:
    def __init__(self):

        self.config = yaml.safe_load(open("conf./conf.yaml"))

        self.race = Race
        self.background = Background
        self.player_class = PlayerClass

        self.stats = dice.generate_stats()
        self.name = names.get_first_name()
        self.prof = mods.plus_or_minus(PROF)
        self.alignment = random.choice(ALIGNMENT)
        self.xp = 0

        self.languages = []
        self.proficiencies = []
        self.skills = []
        self.equipment = []
        self.weapons = []
        self.features = []


def select_item_option(items: list) -> list:
    final_list = []
    weapons = item_dict["weapon"]
    for item in items:
        if "/" in item:
            item_options = item.split("/")
            item = random.choice(item_options)
        if item == "artisan":
            final_list.append(random.choice(item_dict["artisan"]))
        elif item == "instrument":
            final_list.append(random.choice(item_dict["instrument"]))
        elif item == "simple":
            print("simple")
            weapon = random.choice(list(weapons["simple"]))
            print(weapon)
            # final_list.append(weapon)
        elif item == "martial":
            print("martial")
            weapon = random.choice(list(weapons["martial"]))
            print(weapon)
            # final_list.append(weapon)
        else:
            final_list.append(item)
    return final_list


def select_languages(count: int, already_known: list):
    lang_list = []
    while count > 0:
        current_lang = random.choice(LANGUAGES)
        if current_lang not in already_known:
            lang_list.append(current_lang)
            count = count - 1
    return lang_list


def select_race(data: dict, features: list, languages: list) -> dict:
    race = random.choice(list(races_dict))
    race_attributes = races_dict[race]

    data["Race"] = race
    data["Speed"] = race_attributes["speed"]
    racial_modifiers = race_attributes["mods"]

    languages.extend(race_attributes["languages"])
    if "extra_languages" in race_attributes:
        languages.extend(
            select_languages(race_attributes["extra_languages"], languages)
        )

    if race_attributes["darkvision"] == "yes":
        features.append("Darkvision")
    if "Breath Weapon" in race_attributes:
        # TODO
        pass
    if "features" in race_attributes:
        for feature, description in race_attributes["features"].items():
            string = feature + ". " + description
            features.append(string)

    return racial_modifiers


def select_background(data: dict, skills: list, equipment: list, languages: list):
    background = random.choice(list(bg_dict))
    bg_attributes = bg_dict[background]
    char_data["Background"] = background
    equipment.extend(select_item_option(bg_attributes["equipment"]))
    char_data["GP"] = bg_attributes["gp"]

    char_data["PersonalityTraits"] = random.choice(bg_attributes["trait"])
    char_data["Ideals"] = random.choice(bg_attributes["ideal"])
    char_data["Bonds"] = random.choice(bg_attributes["bond"])
    char_data["Flaws"] = random.choice(bg_attributes["flaw"])

    if "languages" in bg_attributes:
        count = bg_attributes["languages"]
        languages.extend(select_languages(count, languages))

    skills.extend(bg_attributes["skills"])


def select_class(
    stats: dict,
    char_data: dict,
    skills: list,
    proficiencies: list,
    equipment: list,
    weapons: list,
):
    player_class = random.choice(list(class_dict))
    class_attributes = class_dict[player_class]
    print(player_class)

    char_data["ClassLevel"] = player_class + " 1"
    char_data["HD"] = "d" + str(class_attributes["hd"])
    char_data["HDTotal"] = "1"
    char_data["HPTemp"] = "0"

    i = 0
    while i < class_attributes["skill number"]:
        skill = random.choice(class_attributes["skills"])
        if skill not in skills:
            skills.append(skill)
            i = i + 1
    skills.extend(class_attributes["saves"])

    ability_modifiers = get_ability_modifiers(stats)
    char_data.update(get_skill_modifiers(skills, ability_modifiers, PROF))
    hit_points = class_attributes["hd"] + ability_modifiers[2]
    char_data["HPMax"] = hit_points
    char_data["HPCurrent"] = hit_points

    proficiencies.extend(select_item_option(class_attributes["prof"]))
    equipment.extend(select_item_option(class_attributes["equipment"]))


def write_fillable_pdf(input_pdf_path: str, output_pdf_path: str, data_dict: dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)

    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1].strip()
                if key in data_dict.keys():
                    if annotation[ANNOT_FORM_type] == ANNOT_FORM_button:
                        # button field i.e. a checkbox
                        annotation.update(
                            pdfrw.PdfDict(
                                V=pdfrw.PdfName(data_dict[key]),
                                AS=pdfrw.PdfName(data_dict[key]),
                            )
                        )
                    elif annotation[ANNOT_FORM_type] == ANNOT_FORM_text:
                        annotation.update(pdfrw.PdfDict(V="{}".format(data_dict[key])))
    template_pdf.Root.AcroForm.update(
        pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject("true"))
    )
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


if __name__ == "__main__":

    # load json dictionaries
    races_dict = load_json(RACE_PATH)
    bg_dict = load_json(BACKGROUND_PATH)
    class_dict = load_json(CLASS_PATH)
    item_dict = load_json(ITEM_PATH)

    racial_mods = select_race(char_data, features, languages)
    select_background(char_data, skills, equipment, languages)
    stats = dice.generate_stats()
    stats = add_racial_mods(stats, racial_mods)
    char_data.update(stats)
    select_class(stats, char_data, skills, proficiencies, equipment, weapons)

    # fill out proficiencies & languages
    char_data["ProficienciesLang"] = (
        ", ".join(languages) + "\n\n" + ", ".join(proficiencies)
    )
    char_data["Equipment"] = ", ".join(equipment)
    char_data["Features and Traits"] = "\r\n".join(features)

    write_fillable_pdf(BLANK_CHAR_SHEET, OUTPUT_CHAR_SHEET, char_data)
