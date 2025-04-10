from dataclasses import dataclass


@dataclass
class Item:
    # From the item table
    item_id: int
    # Unique on creation (except for stackable items) so it's unique in the Inventory
    item_key: str
    slot: str
    name: str
    atk_roll: str
    attack_bonus: int
    ac_bonus: int
    init_bonus: int
    spell_attack_bonus: int
    spell_save: int
    stat_bonuses: dict
    description: str

    def __init__(
        self,
        item_id: int,
        item_key: str,
        slot: str,
        name: str,
        atk_roll: str,
        attack_bonus: int,
        ac_bonus: int,
        init_bonus: int,
        spell_attack_bonus: int,
        spell_save: int,
        stat_bonuses: dict,
        description: str
    ):
        self.item_id = item_id
        self.item_key = item_key
        self.slot = slot
        self.name = name
        self.atk_roll = atk_roll
        self.attack_bonus = attack_bonus
        self.ac_bonus = ac_bonus
        self.init_bonus = init_bonus
        self.spell_attack_bonus = spell_attack_bonus
        self.spell_save = spell_save
        self.stat_bonuses = stat_bonuses
        self.description = description
