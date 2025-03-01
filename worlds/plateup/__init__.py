import random
from dataclasses import dataclass, field
from Options import PerGameCommonOptions
from worlds.AutoWorld import World
from BaseClasses import Region, ItemClassification
from .Items import ITEMS, PlateUpItem
from .Locations import LOCATIONS, DISH_LOCATIONS
from .Options import plateup_options
from .Rules import apply_rules

class PlateUpWorld(World):
    game = "plateup"
    options_dataclass = plateup_options

    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    location_name_to_id = {**LOCATIONS, **DISH_LOCATIONS}

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.progression) -> PlateUpItem:
        """Create a PlateUp item with the given classification."""
        return PlateUpItem(name, classification, self.item_name_to_id[name], self.player)

    def create_items(self):
        """
        This function properly populates the item pool with PlateUp items.
        Ensures items are generated and included in the MultiWorld fill process.
        """
        multiworld = self.multiworld
        player = self.player

        if not hasattr(multiworld.worlds[player], "progression_locations"):
            multiworld.worlds[player].progression_locations = []

        if not hasattr(multiworld.worlds[player], "valid_dish_locations"):
            from .Rules import filter_selected_dishes
            filter_selected_dishes(multiworld, player)  # Run dish filtering

        valid_dish_locations = multiworld.worlds[player].valid_dish_locations
        progression_locations = multiworld.worlds[player].progression_locations

        # Determine minimum required items to fill all valid locations
        min_items_required = len(valid_dish_locations) + len(progression_locations)

        item_pool = []
        item_counts = {}

        # Create all PlateUp-specific items
        for item_name, item_id in self.item_name_to_id.items():
            item = self.create_item(item_name)
            item_pool.append(item)
            item_counts[item_name] = item_counts.get(item_name, 0) + 1

        # Add five "Speed Upgrade Player" items explicitly
        item_pool += [self.create_item("Speed Upgrade Player") for _ in range(5)]

        # Ensure the item count matches the number of locations
        if len(item_pool) < min_items_required:
            filler_needed = min_items_required - len(item_pool)
            for _ in range(filler_needed):
                item_pool.append(self.create_item(self.get_filler_item_name()))

        self.multiworld.itempool += item_pool

        print(f"PlateUp items added: {len(item_pool)}")
        print(f"Total locations to fill: {min_items_required}")
        print(f"Valid Dish Locations: {valid_dish_locations}")
        print(f"Progression Locations: {progression_locations}")

    def create_regions(self):
        from .Regions import create_plateup_regions
        create_plateup_regions(self.multiworld, self.player)

    def set_rules(self):
        """Set progression rules for PlateUp."""
        apply_rules(self.multiworld, self.player)

    def fill_slot_data(self):
        goal_value = self.multiworld.goal[self.player].value
        selected_dishes = list(self.multiworld.selected_dishes.get(self.player, []))

        return {
            "goal": goal_value,
            "selected_dishes": selected_dishes
        }

    def get_filler_item_name(self):
        return "Hob"