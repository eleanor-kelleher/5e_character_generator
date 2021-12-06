import utils
from race import Race
from player_class import PlayerClass
from src import dice
from background import Background


classes = utils.load_json("../data/classes.json")
x = utils.select_random_from_json("../data/races.json")
r = utils.select_random_from_json("../data/backgrounds.json")
b = Background(*r)
a = Race(*x)
y = PlayerClass({"a": "b"}, "Warlock", classes["Warlock"])
s = 4/2
