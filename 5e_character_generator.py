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
ANNOT_KEY = '/Annots'           # key for all annotations within a page
ANNOT_FIELD_KEY = '/T'          # Name of field. i.e. given ID of field
ANNOT_VAL_KEY = '/V'            # Value of field
ANNOT_RECT_KEY = '/Rect'
ANNOT_FORM_type = '/FT'         # Form type (e.g. text/button)
ANNOT_FORM_button = '/Btn'      # ID for buttons, i.e. a checkbox
ANNOT_FORM_text = '/Tx'         # ID for textbox
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'

SKILLS_STR = {"11": "ST Strength", "26": "Athletics"}
SKILLS_DEX = {"18": "ST Dexterity", "23": "Acrobatics", "38": "SleightofHand", "39": "Stealth"}
SKILLS_CON = {"19": "ST Constitution"}
SKILLS_INT = {"20": "ST Intelligence", "25": "Arcana", "28": "History", "31": "Investigation", "33": "Nature", "37": "Religion"}
SKILLS_WIS = {"21": "ST Wisdom", "24": "Animal", "29": "Insight", "32": "Medicine", "34": "Perception", "40": "Survival"}
SKILLS_CHA = {"22": "ST Charisma", "27": "Deception", "30": "Intimidation", "35": "Performance", "36": "Persuasion"}
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
    races_file = open('phbdata/races.json')
    races_dict = json.loads(races_file.read())
    race = random.choice(list(races_dict))
    print(race)
    race_attributes = races_dict[race]
    char_data['Race'] = race
    char_data['Speed'] = race_attributes['speed']

    languages.extend(race_attributes['languages'])
    if 'extra_languages' in race_attributes:
        languages.extend(random_languages(race_attributes['extra_languages'], languages))
    racial_modifiers = race_attributes['mods']
    if race_attributes['darkvision'] == 'yes':
        features.append('Darkvision')
    if "Breath Weapon" in race_attributes:
        # TODO
        pass
    if 'features' in race_attributes:
        for feature, description in race_attributes['features'].items():
            string = feature + ". " + description
            features.append(string)
    races_file.close()
    return racial_modifiers


def random_background():
    bg_file = open('phbdata/backgrounds.json')
    bg_dict = json.loads(bg_file.read())
    background = random.choice(list(bg_dict))
    bg_attributes = bg_dict[background]

    char_data['Background'] = background
    equipment.extend(choose_item_option(bg_attributes['equipment']))
    char_data['GP'] = bg_attributes['gp']

    char_data['PersonalityTraits'] = random.choice(bg_attributes['trait'])
    char_data['Ideals'] = random.choice(bg_attributes['ideal'])
    char_data['Bonds'] = random.choice(bg_attributes['bond'])
    char_data['Flaws'] = random.choice(bg_attributes['flaw'])

    if 'languages' in bg_attributes:
        count = bg_attributes['languages']
        languages.extend(random_languages(count, languages))

    skills.extend(bg_attributes['skills'])
    bg_file.close()


def get_modifier(stat, proficiency=0):
    return math.floor((stat - 10) / 2) + proficiency


def plus_or_minus(mod):
    if mod >= 0:
        return '+' + str(mod)
    return str(mod)


def get_ability_modifiers():
    ability_modifiers = []
    mod_name = ''
    for stat_name, stat_val in stat_dict.items():
        if stat_name == 'CHA':
            mod_name = 'CHamod'
        else:
            mod_name = stat_name + 'mod'
        mod_val = get_modifier(stat_val)
        char_data[mod_name] = plus_or_minus(mod_val)
        ability_modifiers.append(mod_val)
        if mod_name == 'DEXmod':
            char_data['Initiative'] = char_data[mod_name]
    return ability_modifiers


def get_skill_modifiers(prof_skills, ability_modifiers, proficiency):
    for i, mod in enumerate(ability_modifiers):
        for button, skill_name in SKILL_LIST[i].items():
            if skill_name in skills:
                char_data[skill_name] = plus_or_minus(ability_modifiers[i] + proficiency)
                proficiency_button = 'Check Box ' + button
                char_data[proficiency_button] = 'Yes'
                if skill_name == 'Perception':
                    char_data['Passive'] = 10 + ability_modifiers[i] + proficiency
            else:
                char_data[skill_name] = plus_or_minus(ability_modifiers[i])
                if skill_name == 'Perception':
                    char_data['Passive'] = 10 + ability_modifiers[i]


def choose_item_option(item_list):
    final_list = []
    for item in item_list:
        if '/' in item:
            item_options = item.split('/')
            final_list.append(random.choice(item_options))
        else:
            final_list.append(item)
    return final_list


def write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)

    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1].strip()
                if key in data_dict.keys():
                    if annotation[ANNOT_FORM_type] == ANNOT_FORM_button:
                        # button field i.e. a checkbox
                        annotation.update(pdfrw.PdfDict(V=pdfrw.PdfName(data_dict[key]), AS=pdfrw.PdfName(data_dict[key])))
                    elif annotation[ANNOT_FORM_type] == ANNOT_FORM_text:
                        annotation.update(pdfrw.PdfDict(V='{}'.format(data_dict[key])))
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


if __name__ == '__main__':

    char_data = dict()
    languages = []
    proficiencies = []
    skills = []
    equipment = []
    features = []

    char_data['CharacterName'] = names.get_first_name()
    char_data['ProfBonus'] = '+' + str(PROF)
    char_data['Alignment'] = random.choice(ALIGNMENT)
    char_data['XP'] = 0

    racial_mods = random_race()

    stat_dict = generate_stats()
    add_racial_mods(stat_dict, racial_mods)

    random_background()

    # select_class(stat_dict)
    class_file = open('phbdata/classes.json')
    class_dict = json.loads(class_file.read())
    player_class = random.choice(list(class_dict))
    class_attributes = class_dict[player_class]

    char_data['ClassLevel'] = player_class + ' 1'
    char_data['HD'] = 'd' + str(class_attributes['hd'])
    char_data['HDTotal'] = '1'
    char_data['HPTemp'] = '0'

    skills.extend(random.sample(class_attributes['skills'], class_attributes['skill number']))
    skills.extend(class_attributes['saves'])
    print(skills)

    ability_modifiers = get_ability_modifiers()
    get_skill_modifiers(skills, ability_modifiers, PROF)
    hit_points = class_attributes['hd'] + ability_modifiers[2]
    char_data['HPMax'] = hit_points
    char_data['HPCurrent'] = hit_points

    proficiencies.extend(choose_item_option(class_attributes['prof']))
    equipment.extend(choose_item_option(class_attributes['equipment']))

    char_data.update(stat_dict)

    # fill out proficiencies & languages
    char_data['ProficienciesLang'] = ', '.join(languages) + '\n\n' + ', '.join(proficiencies)
    char_data['Equipment'] = ', '.join(equipment)
    char_data['Features and Traits'] = '\r\n'.join(features)

    write_fillable_pdf(BLANK_CHAR_SHEET, OUTPUT_CHAR_SHEET, char_data)
