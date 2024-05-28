from copy import copy
from functools import cached_property
import json
import typing as t
from typing import Any
import pydantic as pd
from rich import print
import pydantic as pd
from rich import print

BM = pd.BaseModel

def F(v):
    # If validate_default is True, then this will raise an exception:
    # Class Foo (BM):
    #   field : str = F(lambda: 1)
    return pd.Field(default_factory=v, validate_default=True)

def Instantiate(args):
    _args = []
    for arg in args:
        # If we got a type, namely a pydantic class,
        # we need to instantiate it, which will force the validation
        # of its fields, which will generate the content
        if isinstance(arg, type) and issubclass(arg, BM):
            _args.append(arg())
        elif callable(arg):
            _args.append(arg())
        # Otherwise, just append the constant values
        else:
            _args.append(arg)
    return _args

def Choice(*args):
    return lambda: r.choice(Instantiate(args))

def Choices(*args, i: int):
    return lambda: r.choices(Instantiate(args), k=i)

def Join(*args: Any, **kwds: Any) -> Any:
    # RECALL: THE INSTANTIATION MUST BE IN THE LAMBDA!
    return lambda: kwds.get("delim", " ").join(Instantiate(args))
    # return lambda: sum(args)

def Seq(*args):
    return lambda: Instantiate(args)

rb = lambda a, b: lambda: r.randint(a,b)
# rr = lambda
# class Join:
#     def __init__(self, item):
#         self._type = item

#     @classmethod
#     def __class_getitem__(cls, item: type):
#         return cls(item)

#     def __call__(self, *args: Any, **kwds: Any) -> Any:
#         args = Instantiate(args)
#         if self._type == str:
#             return lambda: kwds.get("delim", " ").join(args)
#         return lambda: args

"""
* For each model, specify a list of attributes used for its description generation by an LLM
* Each model can also have a "Theme" attribute, which is injected at the beginning of the
context window for the description.
* LLM context can percolate down by generating descriptions based on the current model's attribute selection (generating it from a JSON dump), but also from prepending
the text generations of its parents, to inform this one.

"""

import ollama
import random as r

class MyModel(BM):
    field1: float = F(lambda: r.random())
    field2: str = F(lambda: "a")

class m(BM):
    field1: MyModel = F(MyModel)
    choice: Any = F(Choice(MyModel))
    choices : t.List[MyModel] = F(Choices(MyModel, i=2))
    f : str = F(Join(Choice("Sword", "Mace", "A", "B", "C"), Choice("of", "ov"), "Hell", delim="-"))
    g : t.Sequence[Any] = F(Seq(1,Choice(5,2,7,8),3))


def gen(json, theme, prompt="", modifier="") -> str:
    if not prompt:
        prompt = f"Generate a prose description of this json data representing a game object in a format suitable for rendering directly in a game. Use this theme information to stylize and inform how to render the json as prose. Themes are: {theme}. {json}"
    else:
        prompt = f"{prompt}: use themes of {theme}: {json}"
    if modifier:
        prompt = f"When generating output, modulate this response according to these modifiers: {modifier}. The original request for output is: {prompt}"
    response = ollama.chat(model='llama3', messages=[
    {
        'role': 'user',
        'content': prompt
    },
    {
        "role":"system",
        "content":"Respond to requests as specifically as possible, with absolutely no extraneous commentary or content"
    }
    ])
    return response['message']['content']

class Entity(BM):
    theme : str = ""

    # @property
    # DO NOT INCLUDE THIS ON THE BASE CLASS -- too much compute used;
    # only use it on items you want described!
    # @pd.computed_field
    # def describe(self) -> str:
    #     return gen(self.model_dump_json(exclude="describe"), self.theme)

class VampiricEntity(Entity):
    theme : str = "Vampire, gothic, blood, sex"

class Weapon(Entity):
    name: str = F(Join(Choice("Sword", "Axe", "Mace", "Bow"), "of", Choice("Power", "Strength", "Destruction")))
    damage: int = F(rb(20, 50))
    durability: int = F(rb(50, 100))

class Armor(Entity):
    name: str = F(Join(Choice("Helmet", "Chestplate", "Leggings", "Boots"), "of", Choice("Protection", "Defense", "Resistance")))
    defense: int = F(rb(10, 30))
    durability: int = F(rb(50, 100))

class Potion(Entity):
    name: str = F(Join(Choice("Health", "Mana", "Strength", "Speed"), "Potion"))
    effect: str = F(Choice("Healing", "Boost", "Buff"))
    duration: int = F(rb(10, 30))

class Stats(Entity):
    hp : float = 0.0
    atk : int = 0
    dfs : int = 0
    level: int = 0

class Low(Stats):
    level : int = F(rb(1,5))




class ThemedWeapon(VampiricEntity):
    damage: int = F(rb(20, 50))
    durability: int = F(rb(50, 100))

    # TODO: do we need to exclude all computed fields from ones with dependencies? Likely yes
    # @cached_property
    @pd.computed_field
    def weapon_type(self) -> str:
        weapon_type = Choice("ANY")()
        if weapon_type == "ANY":
            # YOU CANNOT HAVE CIRCULAR DEPENDENCIES.
            # IF A COMPUTED FIELD DOESN'T EXPLICITLY EXCLUDE ANOTHER COMPUTED FIELD,
            # THEN THAT COMPUTED FIELD MUST EXCLUDE IT!
            return gen(self.model_dump_json(exclude={"weapon_type", "name"}), self.theme, prompt="Classify a weapon with these attributes into a weapon type, which is a real type of weapon. It must fit thematically, and must be a realistic object fitting the theme. Respond ONLY with the weapon type.")
        return weapon_type

    # @cached_property
    @pd.computed_field
    def name(self) -> str:
        # Exclude this field, otherwise we have infinite regress
        # and pydantic freaks out and nothing happens when you run.
        # All other dependencies must be excluded!
        return gen(self.model_dump_json(exclude={"name"}), self.theme, prompt="Generate a name for a weapon with these attributes.")

    # CACHED PROPERTY IS NECESSARY SO WE DON'T ENDLESSLY RECOMPUTE COMPUTED FIELDS..... MAYBE
    @cached_property
    @pd.computed_field
    def describe(self) -> str:
        return gen(self.model_dump_json(exclude={"describe"}), self.theme, modifier="One sentence")

class Character(VampiricEntity):
    name: str = F(lambda: "Player")
    stats : Stats = F(lambda: Stats(level=r.randint(1,20)))
    health: int = F(lambda: r.randint(50, 100))
    attack: int = F(lambda: r.randint(10, 20))
    defense: int = F(lambda: r.randint(5, 15))
    weapon : ThemedWeapon = F(ThemedWeapon)
    armor : Armor = F(Armor)
    inventory : t.List[Any] = F(Choices(Weapon, Potion, i=5))

    # Meta fields are for informing generation
    @pd.computed_field(alias="_powerlevel")
    def meta_power_level(self) -> str:
        if self.stats.level < 5:
            return "Weak"
        elif self.stats.level < 10:
            return "Middling"
        elif self.stats.level < 15:
            return "Solid"
        elif self.stats.level < 20:
            return "Godlike"
        return "DEVELOPER"
    # foo : t.Sequence[Any] = F(Seq(Choice()

    @pd.computed_field
    def describe(self) -> str:
        return gen(self.model_dump_json(exclude="describe"), self.theme, modifier="One sentence")
    # @pd.computed_field
    # def hp(self) -> int:
    #     return self.stats.hp
# w = ThemedWeapon()
# # print(w.describe)
# print(w)
# print (m())
c = Character()
print(c)
# print(c.describe)
# print(c)