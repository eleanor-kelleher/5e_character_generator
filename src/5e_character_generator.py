import names
import pdfrw
import random
import yaml

import dice
import mods
import utils

from race import Race
from background import Background
from player_class import PlayerClass

# STATICS
BLANK_CHAR_SHEET = "pdfs/Character Sheet - Form Fillable.pdf"
OUTPUT_CHAR_SHEET = "pdfs/Character_Sheet_Output.pdf"
LANGUAGE_PATH = "../data/languages.json"
BACKGROUND_PATH = "../data/backgrounds.json"
ITEM_PATH = "../data/items.json"


class CharacterSheet:
    def __init__(self):
        self.config = yaml.safe_load(open("../conf/conf.yaml"))
        self.sheet_stuff = utils.load_json("../data/character_stats.json")
        self.all_items = utils.load_json(ITEM_PATH)
        self.c = PlayerClass(*utils.select_random_from_json("../data/classes.json"))
        self.stats = dice.generate_stats()
        self.r = Race(*utils.select_random_from_json("../data/races.json"))
        self.finalise_stats()
        self.b = Background(*utils.select_random_from_json("../data/backgrounds.json"))
        self.character_name = names.get_first_name()
        self.xp = 0

        self.final_languages = self.select_languages()
        self.prof = mods.plus_or_minus(self.sheet_stuff["prof"])
        self.alignment = random.choice(random.choice(self.sheet_stuff["alignment"]))

        # TODO: select skills and proficiencies

        self.proficiencies = []
        self.skills = []

    def finalise_stats(self):
        # Resorting the important stats based on which class was selected
        min_maxed_stats = self.c.min_max_stats
        for idx, stat in enumerate(self.c.min_max_stats):
            if "/" in stat:
                min_maxed_stats[idx] = random.choice(stat.split("/"))
        stats_sorted = sorted((v, k) for k, v in self.stats.items())

        # swaps the top two stat values to the preferred stats
        self.stats[min_maxed_stats[0]], self.stats[stats_sorted[-1][1]] \
            = self.stats[stats_sorted[-1][1]], self.stats[min_maxed_stats[0]]
        self.stats[min_maxed_stats[1]], self.stats[stats_sorted[-2][1]] \
            = self.stats[stats_sorted[-2][1]], self.stats[min_maxed_stats[1]]

        for stat_name in self.stats:
            if stat_name in self.r.mods:
                self.stats[stat_name] = self.stats[stat_name] + self.r.mods[stat_name]

    def select_languages(self):
        all_languages = utils.load_json("../data/languages.json")
        known_languages = self.c.languages + self.r.languages
        # removing possible duplicates from list
        known_languages = list(dict.fromkeys(known_languages))
        extra_languages = self.r.extra_languages + self.b.extra_languages
        if extra_languages == 0:
            return known_languages
        if len(known_languages) + extra_languages >= len(all_languages):
            return all_languages
        for lang in known_languages:
            all_languages.remove(lang)
        return known_languages + random.sample(all_languages, extra_languages)



# def write_fillable_pdf(input_pdf_path: str, output_pdf_path: str, data_dict: dict):
#     template_pdf = pdfrw.PdfReader(input_pdf_path)
#
#     annotations = template_pdf.pages[0][ANNOT_KEY]
#     for annotation in annotations:
#         if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
#             if annotation[ANNOT_FIELD_KEY]:
#                 key = annotation[ANNOT_FIELD_KEY][1:-1].strip()
#                 if key in data_dict.keys():
#                     if annotation[ANNOT_FORM_type] == ANNOT_FORM_button:
#                         # button field i.e. a checkbox
#                         annotation.update(
#                             pdfrw.PdfDict(
#                                 V=pdfrw.PdfName(data_dict[key]),
#                                 AS=pdfrw.PdfName(data_dict[key]),
#                             )
#                         )
#                     elif annotation[ANNOT_FORM_type] == ANNOT_FORM_text:
#                         annotation.update(pdfrw.PdfDict(V="{}".format(data_dict[key])))
#     template_pdf.Root.AcroForm.update(
#         pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject("true"))
#     )
#     pdfrw.PdfWriter().write(output_pdf_path, template_pdf)
#
#
if __name__ == "__main__":
    a = CharacterSheet()
    # racial_mods = select_race(char_data, features, languages)
    # select_background(char_data, skills, equipment, languages)
    # stats = dice.generate_stats()
    # stats = add_racial_mods(stats, racial_mods)
    # char_data.update(stats)
    # select_class(stats, char_data, skills, proficiencies, equipment, weapons)
#
    # # fill out proficiencies & languages
    # char_data["ProficienciesLang"] = (
    #     ", ".join(languages) + "\n\n" + ", ".join(proficiencies)
    # )
    # char_data["Equipment"] = ", ".join(equipment)
    # char_data["Features and Traits"] = "\r\n".join(features)
#
    # write_fillable_pdf(BLANK_CHAR_SHEET, OUTPUT_CHAR_SHEET, char_data)
