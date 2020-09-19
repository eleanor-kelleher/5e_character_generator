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
SKILL_LIST = [SKILLS_STR, SKILLS_DEX, [], SKILLS_INT, SKILLS_WIS, SKILLS_CHA]
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
def stat_gen():
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


def random_background():
    bg_file = open('backgrounds.json')
    bg_dict = json.loads(bg_file.read())
    background = random.choice(list(bg_dict))
    bg_attributes = bg_dict[background]

    char_data['Background'] = background
    equipment.extend(bg_attributes['equipment'])
    char_data['GP'] = bg_attributes['gp']

    if 'languages' in bg_attributes:
        number = bg_attributes['languages']
        while number > 0:
            current_lang = random.choice(LANGUAGES)
            if current_lang not in languages:
                languages.append(current_lang)
                number = number - 1

    bg_file.close()


def write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                if key in data_dict.keys():
                    annotation.update(
                        pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                    )
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


if __name__ == '__main__':

    char_data = dict()
    char_data['CharacterName'] = names.get_first_name()
    char_data['ProfBonus'] = '+' + str(PROF)
    char_data['Alignment'] = random.choice(ALIGNMENT)
    char_data['XP'] = 0

    stat_dict = stat_gen()

    modifiers = []
    mod_name = ''
    for stat_name, stat_val in stat_dict.items():
        if stat_name == 'CHA':
            mod_name = 'CHamod'
        else:
            mod_name = stat_name + 'mod'
        # does not work for DEXmod, unsure why
        mod_val = get_modifier(stat_val)
        char_data[mod_name] = mod_val
        modifiers.append(mod_val)
        if mod_name == 'DEXmod':
            char_data['Initiative'] = char_data[mod_name]


    for i, mod in enumerate(modifiers):
        for j, skill_name in enumerate(SKILL_LIST[i]):
            char_data[skill_name] = modifiers[i]
            print(skill_name, char_data[skill_name])

    languages = []
    proficiencies = []
    equipment = []
    features = []

    random_background()

    # add racial modifiers

    char_data.update(stat_dict)

    # select_class(stat_dict)

    # fill out proficiencies & languages
    lang_list = ', '.join(languages)
    char_data['ProficienciesLang'] = lang_list
    char_data['Equipment'] = ', '.join(equipment)

    write_fillable_pdf(BLANK_CHAR_SHEET, OUTPUT_CHAR_SHEET, char_data)
