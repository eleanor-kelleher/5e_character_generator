import json

import names
import pdfrw
import random
import yaml

import sheet_maths
import utils

from race import Race
from background import Background
from player_class import PlayerClass

# STATICS
BLANK_CHAR_SHEET = "pdfs/CharacterSheet_FormFillable.pdf"
LANGUAGE_PATH = "conf/languages.json"
BACKGROUND_PATH = "conf/backgrounds.json"
ITEM_PATH = "conf/items.json"

ANNOT_KEY = "/Annots"  # key for all annotations within a page
ANNOT_KEY_field = "/T"  # Name of field. i.e. given ID of field
ANNOT_KEY_val = "/V"  # Value of field
ANNOT_KEY_rect = "/Rect"
ANNOT_FORM_type = "/FT"  # Form type (e.g. text/button)
ANNOT_FORM_button = "/Btn"  # ID for buttons, i.e. a checkbox
ANNOT_FORM_text = "/Tx"  # ID for textbox
SUBTYPE_KEY = "/Subtype"
WIDGET_SUBTYPE_KEY = "/Widget"


# TODO: fix cleric subclasses
# TODO: add everything to final data dict


class CharacterSheet:
    def __init__(self):
        self.sheet_stuff = utils.load_json("conf/character_stats.json")
        self.all_items = utils.load_json(ITEM_PATH)
        self.clss = PlayerClass(
            self.sheet_stuff["saving_throws"],
            utils.load_json("conf/items.json"),
            *utils.select_random_from_json("conf/classes.json"),
        )
        self.stats = sheet_maths.generate_stats()
        self.race = Race(*utils.select_random_from_json("conf/races.json"))
        self.finalise_stats()
        self.mods = sheet_maths.generate_mods(self.stats)
        self.saves = sheet_maths.generate_saves(
            self.mods, self.clss.saves, self.clss.proficiency_bonus
        )
        self.bg = Background(*utils.select_random_from_json("conf/backgrounds.json"))
        print(self.clss.class_name, " ", self.race.race_name, " ", self.bg.bg_name)

        self.final_languages = self.select_languages()

        self.final_profs = self.select_profs()
        self.final_skills = self.select_skills()

    def finalise_stats(self):
        # Resorting the important stats based on which class was selected
        min_maxed_stats = self.clss.min_max_stats
        for idx, stat in enumerate(self.clss.min_max_stats):
            if "/" in stat:
                min_maxed_stats[idx] = random.choice(stat.split("/"))
        stats_sorted = sorted((v, k) for k, v in self.stats.items())

        # swaps the top two stat values to the preferred stats
        self.stats[min_maxed_stats[0]], self.stats[stats_sorted[-1][1]] = (
            self.stats[stats_sorted[-1][1]],
            self.stats[min_maxed_stats[0]],
        )
        self.stats[min_maxed_stats[1]], self.stats[stats_sorted[-2][1]] = (
            self.stats[stats_sorted[-2][1]],
            self.stats[min_maxed_stats[1]],
        )

        for stat_name in self.stats:
            if stat_name in self.race.mods:
                self.stats[stat_name] = (
                    self.stats[stat_name] + self.race.mods[stat_name]
                )

    def select_languages(self):
        all_languages = utils.load_json("conf/languages.json")
        known_languages = self.clss.languages + self.race.languages

        # removing possible duplicates from list
        known_languages = list(dict.fromkeys(known_languages))
        extra_languages = self.race.extra_languages + self.bg.extra_languages
        if extra_languages == 0:
            return ", ".join(known_languages)
        if len(known_languages) + extra_languages >= len(all_languages):
            return ", ".join(all_languages)
        for lang in known_languages:
            if lang in all_languages:
                all_languages.remove(lang)
        return ", ".join(
            known_languages + random.sample(all_languages, extra_languages)
        )

    def select_skills(self):
        all_skills = utils.load_json("conf/skills.json")
        known_skills = self.bg.skills + self.race.skills
        # removing any duplicates from the list
        known_skills = list(dict.fromkeys(known_skills))
        skill_options = self.clss.skills
        for skill in known_skills:
            if skill in skill_options:
                skill_options.remove(skill)

        known_skills = known_skills + random.sample(
            skill_options, self.clss.skill_number
        )

        if self.race.skill_number > 0:
            for skill in known_skills:
                all_skills.remove(skill)
            known_skills = known_skills + random.sample(
                all_skills, self.race.skill_number
            )
        return known_skills

    def select_profs(self):
        return ", ".join(
            self.clss.proficiencies + self.bg.proficiencies + self.race.proficiencies
        )

    def create_character_data_dict(self):
        data = {
            "CharacterName": names.get_first_name(),
            "XP": "0",
            "ProfBonus": sheet_maths.plus_or_minus(self.clss.proficiency_bonus),
            "Alignment": random.choice(random.choice(self.sheet_stuff["alignment"])),
            "Initiative": self.mods["DEXmod"],
            "HPMax": self.clss.hit_dice + self.mods["CONmod"],
            "HPCurrent": self.clss.hit_dice + self.mods["CONmod"],
            "ProficienciesLang": self.final_languages + "\n\n" + self.final_profs,
            "Features and Traits": utils.dict_to_string(self.race.features)
            + utils.dict_to_string(self.clss.features),
        }
        # Checking proficient skill boxes
        for skill in self.final_skills:
            data[self.sheet_stuff["skills"][skill]["checkbox"]] = "Yes"
        for skill in self.sheet_stuff["skills"]:
            if skill in self.final_skills:
                data[skill] = sheet_maths.plus_or_minus(
                    self.mods[self.sheet_stuff["skills"][skill]["mod"]]
                    + self.sheet_stuff["prof"]
                )
            else:
                data[skill] = sheet_maths.plus_or_minus(
                    self.mods[self.sheet_stuff["skills"][skill]["mod"]]
                )
        data.update(self.stats)
        data.update(sheet_maths.plus_or_minus_dict(self.mods))
        data.update(sheet_maths.plus_or_minus_dict(self.saves))
        data.update(self.race.race_to_dict())
        data.update(self.bg.bg_to_dict())
        data.update(self.clss.class_to_dict())
        return data

    def write_fillable_pdf(self):
        template_pdf = pdfrw.PdfReader("pdfs/CharacterSheet_FormFillable.pdf")

        data_dict = self.create_character_data_dict()

        annotations = template_pdf.pages[0][ANNOT_KEY]
        for annotation in annotations:
            if annotation["/Subtype"] == WIDGET_SUBTYPE_KEY:
                if annotation[ANNOT_KEY_field]:
                    key = annotation[ANNOT_KEY_field][1:-1].strip()
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
                            annotation.update(
                                pdfrw.PdfDict(V="{}".format(data_dict[key]))
                            )
        template_pdf.Root.AcroForm.update(
            pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject("true"))
        )
        new_pdf_name = f"{data_dict['CharacterName']}_{data_dict['Race'].replace(' ', '-')}" \
                       f"_{data_dict['ClassLevel'][:-3].replace(' ', '-')}" \
                       f"_{data_dict['Background'].replace(' ', '-')}"
        pdfrw.PdfWriter().write(
            f"pdfs/{new_pdf_name}.pdf",
            template_pdf,
        )


if __name__ == "__main__":
    pc = CharacterSheet()
    pc.write_fillable_pdf()
