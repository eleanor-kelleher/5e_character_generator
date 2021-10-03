import math
import random


def get_modifier(stat: int, proficiency: int = 0) -> int:
    return math.floor((stat - 10) / 2) + proficiency


def plus_or_minus(mod: int) -> str:
    if mod >= 0:
        return "+" + str(mod)
    return str(mod)


def add_racial_mods(stats: dict, mods: dict) -> dict:
    for stat_name in stats:
        if stat_name in mods:
            stats[stat_name] = stats[stat_name] + mods[stat_name]

    if "other" in mods:
        count = mods["other"]
        already_added = []
        while count > 0:
            current_stat = random.choice(list(stats))
            if current_stat not in mods and current_stat not in already_added:
                stats[current_stat] = stats[current_stat] + 1
                already_added.append(current_stat)
                count = count - 1
    return stats


def get_ability_modifiers(stats: dict) -> list:
    ability_modifiers = []
    mod_name = ""
    for stat_name, stat_val in stats.items():
        if stat_name == "CHA":
            mod_name = "CHamod"
        else:
            mod_name = stat_name + "mod"
        mod_val = get_modifier(stat_val)
        char_data[mod_name] = plus_or_minus(mod_val)
        ability_modifiers.append(mod_val)
        if mod_name == "DEXmod":
            char_data["Initiative"] = char_data[mod_name]
    return ability_modifiers


def get_skill_modifiers(
    skills: list, ability_modifiers: list, proficiency: int
) -> dict:
    skill_modifiers = dict()
    for i, mod in enumerate(ability_modifiers):
        for button, skill_name in SKILL_LIST[i].items():
            if skill_name in skills:
                skill_modifiers[skill_name] = plus_or_minus(
                    ability_modifiers[i] + proficiency
                )
                proficiency_button = "Check Box " + button
                skill_modifiers[proficiency_button] = "Yes"
                if skill_name == "Perception":
                    skill_modifiers["Passive"] = 10 + ability_modifiers[i] + proficiency
            else:
                skill_modifiers[skill_name] = plus_or_minus(ability_modifiers[i])
                if skill_name == "Perception":
                    skill_modifiers["Passive"] = 10 + ability_modifiers[i]
    return skill_modifiers
