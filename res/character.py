from dataclasses import dataclass
from .equipment import Equipment
from .inventory import Inventory
from .item import Item
import json


@dataclass
class Character:
    name: str
    job: str
    lvl: int
    hp: int
    strength: int
    dex: int
    con: int 
    cha: int
    intel: int
    wis: int
    intel: int
    ac: int
    initiative: int
    inventory: Inventory
    equipment: Equipment

    def __init__(self, name: str, job: str, lvl:int, hp: int, strength: int, dex: int, con: int, cha: int, wis: int, intel: int, ac: int, initiative: int, inventory: Inventory, equipment: Equipment):
        self.name = name 
        self.job = job 
        self.lvl = lvl
        self.hp = hp
        self.strength = strength
        self.dex = dex
        self.con = con
        self.cha = cha 
        self.wis = wis 
        self.intel = intel
        self.ac = ac
        self.initiative = initiative
        self.inventory = inventory
        self.equipment = equipment
    
    def initial_stat_calculations(self):
        for item in self.equipment:
            pass
    
    def attack_roll(self, equipment: Equipment):
        pass

# Pull the character's JSON file from the characters/ directory
def from_file(character_name: str) -> Character:
    file_name = "characters/" + character_name + ".json"
    name = ""
    job = ""
    lvl = 0
    hp = 0
    strength = 0
    dex = 0
    con = 0
    cha = 0
    wis = 0
    intel = 0
    ac = 10
    initiative = 0
    starting_equipment = []
    inventory = Inventory([])
    with open(file_name) as f_in:
        character_json = json.load(f_in)
        name = character_json["name"]
        job = character_json["job"]
        lvl = character_json["lvl"]
        hp = character_json["hp"]
        strength = character_json["strength"]
        dex = character_json["dex"]
        con = character_json["con"]
        cha = character_json["cha"]
        wis = character_json["wis"]
        intel = character_json["intel"]
        starting_equipment = character_json["starting_equipment"]
    with open("res/items.json") as f_in:
        items_json = json.load(f_in)
        for item_id in starting_equipment:
            item_json = items_json[str(item_id)]
            item_slot = item_json["slot"]
            item_name = item_json["name"]
            item_atk_roll = item_json["atk_roll"]
            item_attack_bonus = item_json["attack_bonus"]
            item_ac_bonus = item_json["ac_bonus"]
            item_init_bonus = item_json["init_bonus"]
            item_spell_attack_bonus = item_json["spell_attack_bonus"]
            item_spell_save = item_json["spell_save"]
            item_stat_bonuses = item_json["stat_bonuses"]
            item_description = item_json["description"]
            new_item = Item(item_id, "", item_slot, item_name, item_atk_roll, item_attack_bonus, item_ac_bonus, item_init_bonus, item_spell_attack_bonus, item_spell_save, item_stat_bonuses, item_description)
            inventory.add_item(new_item)
    helmet = None
    chest = None
    arms = None
    legs = None
    amulet = None
    ring1 = None
    ring2 = None
    weapon = None
    for item in inventory:
        if item.slot == "helmet":
            helmet = item
        elif item.slot == "chest":
            chest = item
        elif item.slot == "arms":
            arms = item
        elif item.slot == "legs":
            legs = item
        elif item.slot == "amulet":
            amulet = item
        elif item.slot == "ring1":
            ring1 = item
        elif item.slot == "ring2":
            ring2 = item
        elif item.slot == "weapon":
            weapon = item
    equipment = Equipment(
        helmet=helmet,
        chest=chest,
        arms=arms,
        legs=legs,
        amulet=amulet,
        ring1=ring1,
        ring2=ring2,
        weapon=weapon
    )
    new_character = Character(name, job, lvl, hp, strength, dex, con, cha, wis, intel, ac, initiative, inventory, equipment)
    new_character.initial_stat_calculations()
    return new_character

