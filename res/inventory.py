from dataclasses import dataclass
from .item import Item


@dataclass
class Inventory:
    items: list

    def __init__(self, items: list):
        self.items = items 
    
    def add_item(self, item: Item):
        self.items.append(item)
    
    def remove_item(self, item: Item):
        # Remove from inventory by item_id
        pass

    def get_total_unique_items(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)
