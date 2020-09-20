import json
import math
import names
import pdfrw
import random

# STATICS
BLANK_CHAR_SHEET = 'Character Sheet - Form Fillable.pdf'
OUTPUT_CHAR_SHEET = 'Character_Sheet_Output.pdf'
PROF = 2
ALIGNMENT = ['LG', 'NG', 'CG', 'LN', 'N', 'CN', 'LE', 'NE', 'CE']
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'

SKILLS_STR = ["ST Strength", "Athletics"]
SKILLS_DEX = ["ST Dexterity", "Acrobatics", "SleightofHand", "Stealth"]
SKILLS_CON = ["ST Constitution"]
SKILLS_INT = ["ST Intelligence", "Arcana", "History", "Investigation", "Nature", "Religion"]
SKILLS_WIS = ["ST Wisdom", "Animal", "Insight", "Medicine", "Perception", "Survival"]
SKILLS_CHA = ["ST Charisma", "Deception", "Intimidation", "Performance", "Persuasion"]
SKILL_LIST = [SKILLS_STR, SKILLS_DEX, SKILLS_CON, SKILLS_INT, SKILLS_WIS, SKILLS_CHA]
LANGUAGES = ["Common", "Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin", "Halfling",
             "Orc", "Abyssal", "Celestial", "Draconic", "Deep Speech", "Infernal",
             "Primordial", "Sylvan", "Undercommon"]


def d6():
    return random.randint(1, 6)


def drop_lowest(roll_list):
    min_stat = roll_list[0]
    min_i = 0
    for i, roll in enumerate(roll_list):
        if roll < min_stat:
            min_stat = roll
            min_i = i
    del roll_list[min_i]
    return roll_list


def drop_lowest_in_dict(roll_list):
    min_stat = roll_list[0]
    min_i = 0
    for i, roll in enumerate(roll_list):
        if roll < min_stat:
            min_stat = roll
            min_i = i
    del roll_list[min_i]
    return roll_list


# convention is 4d6, drop the lowest
def roll_one_stat():
    all_rolls = [d6(), d6(), d6(), d6()]
    good_rolls = drop_lowest(all_rolls)
    return sum(good_rolls)


# takes 7 stats, keeps highest 6
def generate_stats():
    seven_stats = [roll_one_stat(), roll_one_stat(), roll_one_stat(), roll_one_stat(),
                   roll_one_stat(), roll_one_stat(), roll_one_stat()]
    six_stats = drop_lowest(seven_stats)
    return {'STR': six_stats[0],
            'DEX': six_stats[1],
            'CON': six_stats[2],
            'INT': six_stats[3],
            'WIS': six_stats[4],
            'CHA': six_stats[5]}


def get_modifier(stat, proficiency=0):
    mod = math.floor((stat - 10) / 2) + proficiency
    if mod >= 0:
        return '+' + str(mod)
    return str(mod)


def add_racial_mods(stats, mods):
    for stat_name in stats:
        if stat_name in mods:
            stats[stat_name] = stats[stat_name] + mods[stat_name]

    if 'other' in mods:
        count = mods['other']
        already_added = []
        while count > 0:
            current_stat = random.choice(list(stats))
            if current_stat not in mods and current_stat not in already_added:
                stats[current_stat] = stats[current_stat] + 1
                already_added.append(current_stat)
                count = count - 1


def random_languages(count, already_known):
    lang_list = []
    while count > 0:
        current_lang = random.choice(LANGUAGES)
        if current_lang not in already_known:
            lang_list.append(current_lang)
            count = count - 1
    return lang_list


def random_race():
    races_file = open('races.json')
    races_dict = json.loads(races_file.read())
    race = random.choice(list(races_dict))
    print(race)
    race_attributes = races_dict[race]
    char_data['Race'] = race
    char_data['Speed'] = race_attributes['speed']

    languages.extend(race_attributes['languages'])
    if 'extra_languages' in race_attributes:
        languages.extend(random_languages(race_attributes['extra_languages'], languages))
    racial_mods = race_attributes['mods']
    if race_attributes['darkvision'] == 'yes':
        features.append('Darkvision')
    if "Breath Weapon" in race_attributes:
        # TODO
        pass
    if 'features' in race_attributes:
        for feature, description in race_attributes['features'].items():
            print(feature, description)
            string = feature + ". " + description
            features.append(string)
    races_file.close()
    return racial_mods


def random_background():
    bg_file = open('backgrounds.json')
    bg_dict = json.loads(bg_file.read())
    background = random.choice(list(bg_dict))
    bg_attributes = bg_dict[background]

    char_data['Background'] = background
    equipment.extend(bg_attributes['equipment'])
    char_data['GP'] = bg_attributes['gp']

    char_data['PersonalityTraits'] = random.choice(bg_attributes['trait'])
    char_data['Ideals'] = random.choice(bg_attributes['ideal'])
    char_data['Bonds'] = random.choice(bg_attributes['bond'])
    char_data['Flaws'] = random.choice(bg_attributes['flaw'])

    if 'languages' in bg_attributes:
        count = bg_attributes['languages']
        languages.extend(random_languages(count, languages))
    bg_file.close()


def write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1].strip()
                if key in data_dict.keys():
                    annotation.update(pdfrw.PdfDict(V='{}'.format(data_dict[key])))
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


if __name__ == '__main__':

    char_data = dict()
    racial_mods = dict()
    languages = []
    proficiencies = []
    equipment = []
    features = []

    char_data['CharacterName'] = names.get_first_name()
    char_data['ProfBonus'] = '+' + str(PROF)
    char_data['Alignment'] = random.choice(ALIGNMENT)
    char_data['XP'] = 0

    racial_mods = random_race()

    stat_dict = generate_stats()
    add_racial_mods(stat_dict, racial_mods)

    modifiers = []
    mod_name = ''
    for stat_name, stat_val in stat_dict.items():
        if stat_name == 'CHA':
            mod_name = 'CHamod'
        else:
            mod_name = stat_name + 'mod'
        mod_val = get_modifier(stat_val)
        char_data[mod_name] = mod_val
        modifiers.append(mod_val)
        if mod_name == 'DEXmod':
            char_data['Initiative'] = char_data[mod_name]

    for i, mod in enumerate(modifiers):
        for j, skill_name in enumerate(SKILL_LIST[i]):
            char_data[skill_name] = modifiers[i]
            # print(skill_name, char_data[skill_name])

    random_background()

    # add racial modifiers

    char_data.update(stat_dict)

    # select_class(stat_dict)

    # fill out proficiencies & languages
    lang_list = ', '.join(languages)
    char_data['ProficienciesLang'] = lang_list
    char_data['Equipment'] = ', '.join(equipment)
    char_data['Features and Traits'] = '\r\n'.join(features)

    # for x, y in char_data.items():
    #     print(x, y)

    write_fillable_pdf(BLANK_CHAR_SHEET, OUTPUT_CHAR_SHEET, char_data)
