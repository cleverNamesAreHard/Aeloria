from dataclasses import dataclass
from .inventory import Inventory
from .item import Item
import json


@dataclass
class Character:
    name: str
    job: str
    hp: int
    atk: int 
    mag: int
    defs: int
    mdef: int
    inventory: Inventory

    def __init__(self, name: str, job: str, hp: int, atk: int, mag: int, defs: int, mdef: int, inventory: Inventory):
        self.name = name 
        self.job = job 
        self.hp = hp 
        self.atk = atk
        self.mag = mag 
        self.defs = defs 
        self.mdef = mdef
        self.inventory = inventory
    
    def attack_roll(self, inventory: Inventory):
        pass

# Pull the character's JSON file from the characters/ directory
def from_file(character_name: str) -> Character:
    file_name = "characters/" + character_name + ".json"
    name = ""
    job = ""
    hp = 0
    atk = 0
    mag = 0
    defs = 0
    mdef = 0
    inventory = Inventory([])
    with open(file_name) as f_in:
        character_json = json.load(f_in)
        name = character_json["name"]
        job = character_json["job"]
        hp = character_json["hp"]
        atk = character_json["atk"]
        mag = character_json["mag"]
        defs = character_json["defs"]
        mdef = character_json["mdef"]
        for equipment in character_json["starting_equipment"]:
            item_id = equipment["item_id"]
            item_slot = equipment["slot"]
            item_name = equipment["name"]
            item_atk = equipment["atk"]
            item_mag = equipment["mag"]
            item_defs = equipment["defs"]
            item_mdefs = equipment["mdefs"]
            new_item = Item(item_id, "", item_slot, item_name, item_atk, item_mag, item_defs, item_mdefs)
            inventory.add_item(new_item)
    new_character = Character(name, job, hp, atk, mag, defs, mdef, inventory)
    return new_character

