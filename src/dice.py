import random


def d6() -> int:
    return random.randint(1, 6)


def drop_lowest(rolls: list) -> list:
    min_stat = rolls[0]
    min_i = 0
    for i, roll in enumerate(rolls):
        if roll < min_stat:
            min_stat = roll
            min_i = i
    del rolls[min_i]
    return rolls


# convention is 4d6, drop the lowest
def roll_one_stat() -> int:
    all_rolls = [d6(), d6(), d6(), d6()]
    good_rolls = drop_lowest(all_rolls)
    return sum(good_rolls)


# takes 7 stats, keeps highest 6
def generate_stats() -> dict:
    seven_stats = [roll_one_stat() for i in range(7)]
    six_stats = drop_lowest(seven_stats)
    stat_keys = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    return dict(zip(stat_keys, six_stats))


def generate_mods(stats: dict):
    mods = {}
    for stat in stats:
        mods[stat + "mod"] = (stats[stat] - 10) // 2
    mods["CHamod"] = mods["CHAmod"]
    return mods


def generate_saves(mods: dict, proficient_saves: dict, proficiency_bonus: int):
    save_keys = ["ST Strength", "ST Dexterity", "ST Constitution",
                 "ST Intelligence", "ST Wisdom", "ST Charisma"]
    saves = dict(zip(save_keys, mods.values()))
    for save_key in proficient_saves:
        saves[save_key] = saves[save_key] + proficiency_bonus
    return saves
