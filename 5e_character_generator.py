import os
import pdfrw
import random

# STATICS
BLANK_CHAR_SHEET = 'Character_Sheet.pdf'
OUTPUT_CHAR_SHEET = 'Character_Sheet_Output.pdf'
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'


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


# convention is 4d6, drop the lowest
def dice_roll():
    all_rolls = [d6(), d6(), d6(), d6()]
    good_rolls = drop_lowest(all_rolls)
    return sum(good_rolls)


# takes 7 stats, keeps highest 6
def stat_gen():
    seven_stats = [dice_roll(), dice_roll(), dice_roll(), dice_roll(),
                   dice_roll(), dice_roll(), dice_roll()]
    six_stats = drop_lowest(seven_stats)
    return {'s_str': six_stats[0],
            's_dex': six_stats[1],
            's_con': six_stats[2],
            's_int': six_stats[3],
            's_wis': six_stats[4],
            's_cha': six_stats[5]}


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


if __name__ == "__main__":

    data = dict()
    stat_dict = stat_gen()
    data.update(stat_dict)
    write_fillable_pdf(BLANK_CHAR_SHEET, OUTPUT_CHAR_SHEET, data)
