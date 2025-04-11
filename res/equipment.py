from dataclasses import dataclass
from .item import Item


@dataclass
class Equipment:
    helmet: Item
    chest: Item
    arms: Item
    legs: Item
    amulet: Item
    ring1: Item
    ring2: Item
    weapon: Item

    def __init__(self, helmet: Item, chest: Item, arms: Item, legs: Item, amulet: Item, ring1: Item, ring2: Item, weapon: Item):
        self.helmet = helmet
        self.chest = chest
        self.arms = arms
        self.legs = legs
        self.amulet = amulet
        self.ring1 = ring1
        self.ring2 = ring2
        self.weapon = weapon

    def __iter__(self):
        return iter([
            self.helmet,
            self.chest,
            self.arms,
            self.legs,
            self.amulet,
            self.ring1,
            self.ring2,
            self.weapon
        ])
