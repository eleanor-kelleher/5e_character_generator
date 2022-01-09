import utils
from race import Race
from player_class import PlayerClass
from src import sheet_maths
from background import Background


classes = utils.load_json("../conf/classes.json")
x = utils.select_random_from_json("../conf/races.json")
r = utils.select_random_from_json("../conf/backgrounds.json")
b = Background(*r)
a = Race(*x)
y = PlayerClass({"a": "b"}, "Warlock", classes["Warlock"])
s = 4/2
