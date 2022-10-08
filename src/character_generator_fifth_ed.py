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

# TODO 2: Add AC
# TODO 2.5: Improve logging
# TODO 3: Fix cleric subclasses


class CharacterSheet:
    def __init__(self):
        with open("conf/filepaths.yaml") as filepath_config:
            self.conf = yaml.safe_load(filepath_config)
        self.sheet_stuff = utils.load_json(self.conf["CHARACTER_STATS_PATH"])
        self.all_items = utils.load_json(self.conf["ITEM_PATH"])
        self.clss = PlayerClass(
            self.sheet_stuff["saving_throws"],
            utils.load_json(self.conf["ITEM_PATH"]),
            *utils.select_random_from_json(self.conf["PLAYER_CLASS_PATH"]),
        )
        self.stats = sheet_maths.generate_stats()
        self.race = Race(*utils.select_random_from_json(self.conf["RACES_PATH"]))
        self.finalise_stats()
        self.mods = sheet_maths.generate_mods(self.stats)
        self.saves = sheet_maths.generate_saves(
            self.mods, self.clss.saves, self.clss.proficiency_bonus
        )
        self.weapons = self.finalise_weapons()
        self.bg = Background(
            *utils.select_random_from_json(self.conf["BACKGROUND_PATH"])
        )
        self.final_languages = self.select_languages()

        self.final_profs = self.select_profs()
        self.final_skills = self.select_skills()
        self.ac = self.finalise_ac()
        if "Perception" in self.final_skills:
            self.pp = self.mods["WISmod"] + self.clss.proficiency_bonus + 10
        else:
            self.pp = self.mods["WISmod"] + 10

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
        all_languages = utils.load_json(self.conf["LANGUAGE_PATH"])
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
        all_skills = utils.load_json(self.conf["SKILLS_PATH"])
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

    def finalise_weapons(self):
        final_weapon_dict = {"AttacksSpellcasting": ""}
        for i, weapon in enumerate(self.clss.weapons):
            if self.clss.weapons[i]["melee"] == "no" or (
                self.clss.weapons[i]["finesse"] == "yes"
                and self.mods["DEXmod"] >= self.mods["STRmod"]
            ):
                str_or_dex = "DEXmod"
            else:
                str_or_dex = "STRmod"
            if i < 3:
                num = str(i + 1)
                if i == 0:
                    final_weapon_dict["Wpn Name"] = self.clss.weapons[i]["name"]
                else:
                    final_weapon_dict["Wpn Name " + num] = self.clss.weapons[i]["name"]
                final_weapon_dict[
                    f"Wpn{num} AtkBonus"
                ] = f"+{self.clss.proficiency_bonus + self.mods[str_or_dex]}"
                final_weapon_dict[
                    f"Wpn{num} Damage"
                ] = f"{self.clss.weapons[i]['dmg']}+{self.mods[str_or_dex]}"
            else:
                final_weapon_dict["AttacksSpellcasting"] = (
                    f"{final_weapon_dict['AttacksSpellcasting']}{self.clss.weapons[i]['name']} "
                    f"+{self.clss.proficiency_bonus + self.mods[str_or_dex]} "
                    f"{self.clss.weapons[i]['dmg']}+{self.mods[str_or_dex]}\n"
                )

        return final_weapon_dict

    def finalise_ac(self):
        if self.clss.ac == "" and self.clss.armors:
            ac = 0
            for armor in self.clss.armors:
                if (
                    armor["plus_dex"] == "yes"
                    and armor["two_dex_max"] == "yes"
                    and self.mods["DEXmod"] > 2
                ):
                    ac = ac + armor["base"] + 2
                elif armor["plus_dex"] == "yes":
                    ac = ac + armor["base"] + self.mods["DEXmod"]
                else:
                    ac = ac + armor["base"]
            return ac
        if self.clss.class_name == "Barbarian":
            return 10 + self.mods["DEXmod"] + self.mods["CONmod"]
        if (
            self.clss.class_name == "Sorcerer"
            and self.clss.subclass == "Draconic Bloodline"
        ):
            return 13 + self.mods["DEXmod"]

        return 10 + self.mods["DEXmod"]

    def create_character_data_dict(self, player_name: str = ""):
        data = {
            "CharacterName": names.get_first_name(),
            "XP": "0",
            "ProfBonus": sheet_maths.plus_or_minus(self.clss.proficiency_bonus),
            "Alignment": random.choice(random.choice(self.sheet_stuff["alignment"])),
            "Initiative": sheet_maths.plus_or_minus(self.mods["DEXmod"]),
            "HPMax": self.clss.hit_dice + self.mods["CONmod"],
            "HPCurrent": self.clss.hit_dice + self.mods["CONmod"],
            "Equipment": ", ".join(self.bg.equipment + self.clss.equipment),
            "ProficienciesLang": self.final_languages + "\n\n" + self.final_profs,
            "Features and Traits": utils.dict_to_string(self.race.features)
            + utils.dict_to_string(self.clss.features),
            "Passive": str(self.pp),
            "AC": self.ac,
        }

        if player_name:
            data["PlayerName"] = player_name

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
        data.update(self.weapons)
        return data

    def write_fillable_pdf(self, data_dict: dict):
        template_pdf = pdfrw.PdfReader(self.conf["BLANK_CHAR_SHEET"])

        annotations = template_pdf.pages[0][self.conf["ANNOT_KEY"]]
        for annotation in annotations:
            if annotation["/Subtype"] == self.conf["WIDGET_SUBTYPE_KEY"]:
                if annotation[self.conf["ANNOT_KEY_field"]]:
                    key = annotation[self.conf["ANNOT_KEY_field"]][1:-1].strip()
                    if key in data_dict.keys():
                        if (
                            annotation[self.conf["ANNOT_FORM_type"]]
                            == self.conf["ANNOT_FORM_button"]
                        ):
                            # button field i.e. a checkbox
                            annotation.update(
                                pdfrw.PdfDict(
                                    V=pdfrw.PdfName(data_dict[key]),
                                    AS=pdfrw.PdfName(data_dict[key]),
                                )
                            )
                        elif (
                            annotation[self.conf["ANNOT_FORM_type"]]
                            == self.conf["ANNOT_FORM_text"]
                        ):
                            annotation.update(
                                pdfrw.PdfDict(V="{}".format(data_dict[key]))
                            )
        template_pdf.Root.AcroForm.update(
            pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject("true"))
        )
        new_pdf_name = (
            f"pdfs/{data_dict['CharacterName']}_{data_dict['Race'].replace(' ', '-')}"
            f"_{data_dict['ClassLevel'][:-3].replace(' ', '-')}"
            f"_{data_dict['Background'].replace(' ', '-')}.pdf"
        )
        pdfrw.PdfWriter().write(
            new_pdf_name,
            template_pdf,
        )
        return new_pdf_name