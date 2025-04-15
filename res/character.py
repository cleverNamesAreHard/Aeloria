from dataclasses import dataclass
from .equipment import Equipment
from .inventory import Inventory
from .item import Item
import json
import os
import random
import re


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
    ac: int
    initiative: int
    inventory: Inventory
    equipment: Equipment
    role: str  # 'starter', 'enemy', 'enemy_hero', 'ally', etc.
    attack_ids: list  # List of IDs referring to entries in attacks.json

    def __init__(self, name: str, job: str, lvl: int, hp: int, strength: int, dex: int, con: int, cha: int, wis: int, intel: int, ac: int, initiative: int, inventory: Inventory, equipment: Equipment, role: str, attack_ids: list):
        self.name = name
        self.job = job
        self.lvl = lvl
        self.hp = hp
        self.current_hp = hp
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
        self.role = role
        self.attack_ids = attack_ids

    def initial_stat_calculations(self):
        for item in self.equipment:
            if item:
                self.ac += item.ac_bonus
                self.initiative += item.init_bonus

    def attack_roll(self, equipment: Equipment):
        if equipment and equipment.atk_roll:
            total, breakdown = evaluate_expression(equipment.atk_roll)
            print(f"{self.name} rolls with weapon: {breakdown} = {total}")
            return total
        else:
            print(f"{self.name} has no weapon attack roll.")
            return 0


def load_character_by_name(character_name: str, campaign_name: str):
    path = os.path.join("campaigns", campaign_name, "characters.json")
    with open(path) as f:
        characters = json.load(f)
    match = next((char for char in characters if char.get("name") == character_name), None)
    if not match:
        raise ValueError(f"Character with name '{character_name}' not found.")
    return _create_character_from_dict(match, campaign_name)


def _create_character_from_dict(character_data: dict, campaign_name: str):
    name = character_data["name"]
    job = character_data["job"]
    lvl = character_data["lvl"]
    hp = character_data["hp"]
    strength = character_data["strength"]
    dex = character_data["dex"]
    con = character_data["con"]
    cha = character_data["cha"]
    wis = character_data["wis"]
    intel = character_data["intel"]
    starting_equipment = character_data["starting_equipment"]
    role = character_data.get("role", "starter")
    attack_ids = character_data.get("attacks", [])

    ac = 10
    initiative = 0
    inventory = Inventory([])

    items_path = os.path.join("campaigns", campaign_name, "items.json")
    with open(items_path) as f_in:
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

            new_item = Item(
                item_id,
                "",
                item_slot,
                item_name,
                item_atk_roll,
                item_attack_bonus,
                item_ac_bonus,
                item_init_bonus,
                item_spell_attack_bonus,
                item_spell_save,
                item_stat_bonuses,
                item_description
            )
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

    new_character = Character(
        name,
        job,
        lvl,
        hp,
        strength,
        dex,
        con,
        cha,
        wis,
        intel,
        ac,
        initiative,
        inventory,
        equipment,
        role,
        attack_ids
    )
    new_character.initial_stat_calculations()
    return new_character


def roll_die(num_rolls, die_size):
    return [random.randint(1, die_size) for _ in range(num_rolls)]


def evaluate_expression(expression):
    expression = re.sub(r"\s+", "", expression)  # Strip all spaces
    tokens = re.findall(r"[-+]?(?:\d*d\d+|\d+)", expression)

    total = 0
    breakdown = []

    for token in tokens:
        operator = "+" if token[0] not in "-+" else token[0]
        token = token.lstrip("+-")

        if "d" in token:
            num_rolls, die_size = token.split("d")
            num_rolls = int(num_rolls) if num_rolls else 1
            die_size = int(die_size)
            rolls = roll_die(num_rolls, die_size)
            result = sum(rolls)
            breakdown.append(f"{operator} ({' + '.join(map(str, rolls))})")
        else:
            result = int(token)
            breakdown.append(f"{operator} {result}")

        if operator == "+":
            total += result
        else:
            total -= result

    breakdown_string = " ".join(breakdown).lstrip("+ ")
    return total, breakdown_string
