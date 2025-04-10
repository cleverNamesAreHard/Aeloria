from dataclasses import dataclass


@dataclass
class Item:
    # From the item table
    item_id: int
    # Unique on creation (except for stackable items) so it's unique in the Inventory
    item_key: str
    slot: str
    name: str
    atk: int 
    mag: int
    defs: int
    mdef: int

    def __init__(self, item_id: int, item_key: str, slot: str, name: str, atk: int, mag: int, defs: int, mdef: int):
        self.item_id = item_id
        self.item_key = item_key
        self.slot = slot
        self.name = name
        self.atk = atk 
        self.mag = mag 
        self.defs = defs
        self.mdef = mdef